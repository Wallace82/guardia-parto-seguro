"""
GuardIA — Audit Service
"""
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.audit.models import AuditLog

log = structlog.get_logger(__name__)

class AuditService:
    @staticmethod
    async def log_action(
        db: AsyncSession,
        action: str,
        resource: str,
        user_id: int | None = None,
        ip_address: str | None = None,
        details: dict | None = None,
    ):
        """Registra uma ação de auditoria no banco de forma imutável."""
        try:
            audit_entry = AuditLog(
                user_id=user_id,
                action=action,
                resource=resource,
                ip_address=ip_address,
                details=details or {},
            )
            db.add(audit_entry)
            # Não fazemos commit aqui, deixamos a sessão atual commitar ou usamos flush.
            # O get_db do FastAPI já faz o commit no final do request com sucesso.
        except Exception as e:
            log.error("audit_log_failed", error=str(e), action=action, resource=resource)
