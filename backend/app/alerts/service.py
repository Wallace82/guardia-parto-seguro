"""
GuardIA — Alerts Service
Criação, listagem e reconhecimento de alertas + notificação por e-mail
"""
from datetime import datetime, timezone

import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import structlog
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.alerts.models import Alert, AlertSeverity
from app.alerts.schemas import AlertCreateRequest
from app.config import settings

log = structlog.get_logger(__name__)


class AlertService:
    """Gerencia o ciclo de vida dos alertas de risco assistencial."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_alert(self, data: AlertCreateRequest) -> Alert:
        """
        Cria um alerta. Se severity=critical, dispara e-mail automático.
        Chamado internamente pelo motor de risco (risk-service via core-api).
        """
        alert = Alert(
            session_id=data.session_id,
            alert_type=data.alert_type,
            severity=data.severity,
            title=data.title,
            description=data.description,
            ira_score=data.ira_score,
        )
        self.db.add(alert)
        await self.db.flush()

        # Notificação automática para alertas críticos
        if data.severity == AlertSeverity.critical:
            await self._send_critical_email(alert)

        return alert

    async def list_alerts(
        self,
        user_role: str,
        session_id: int | None = None,
        severity: str | None = None,
        unacknowledged_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[int, list[Alert]]:
        """Lista alertas com filtros opcionais."""
        query = select(Alert)

        if session_id:
            query = query.where(Alert.session_id == session_id)
        if severity:
            query = query.where(Alert.severity == severity)
        if unacknowledged_only:
            query = query.where(Alert.is_acknowledged.is_(False))

        query = query.order_by(Alert.created_at.desc())

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        result = await self.db.execute(query.offset(skip).limit(limit))
        items = list(result.scalars().all())

        return total, items

    async def acknowledge(self, alert_id: int, acknowledged_by_id: int) -> Alert:
        """Marca alerta como reconhecido pelo profissional/gestor."""
        result = await self.db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()

        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alerta não encontrado",
            )
        if alert.is_acknowledged:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Alerta já foi reconhecido",
            )

        alert.is_acknowledged = True
        alert.acknowledged_by = acknowledged_by_id
        alert.acknowledged_at = datetime.now(timezone.utc)
        return alert

    async def _send_critical_email(self, alert: Alert) -> None:
        """
        Envia e-mail de alerta crítico para o gestor.
        Falhas são logadas mas não propagadas (fire-and-forget).
        """
        if not settings.SMTP_HOST or not settings.ALERT_EMAIL_GESTOR:
            log.warning("email_not_configured", alert_id=alert.id)
            return

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"🚨 GuardIA — ALERTA CRÍTICO | Sessão #{alert.session_id}"
            msg["From"] = f"GuardIA Parto Seguro <{settings.SMTP_USER}>"
            msg["To"] = settings.ALERT_EMAIL_GESTOR

            html_body = f"""
            <html><body>
            <h2 style="color:#dc2626;">🚨 Alerta Crítico Detectado</h2>
            <p><strong>Sessão:</strong> #{alert.session_id}</p>
            <p><strong>Tipo:</strong> {alert.alert_type}</p>
            <p><strong>Título:</strong> {alert.title}</p>
            <p><strong>Descrição:</strong> {alert.description}</p>
            <p><strong>Score IRA:</strong> {alert.ira_score or "N/A"}</p>
            <p><strong>Data/Hora:</strong> {alert.created_at}</p>
            <hr>
            <p style="color:#6b7280;font-size:12px;">
            Este é um alerta automático do GuardIA Parto Seguro.
            Acesse o dashboard para reconhecer este alerta.
            </p>
            </body></html>
            """
            msg.attach(MIMEText(html_body, "html"))

            await aiosmtplib.send(
                msg,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=True,
            )
            alert.email_sent = True
            log.info("critical_alert_email_sent", alert_id=alert.id, to=settings.ALERT_EMAIL_GESTOR)
        except Exception as exc:
            log.error("critical_alert_email_failed", alert_id=alert.id, error=str(exc))
