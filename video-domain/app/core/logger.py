"""
GuardIA — Video Domain — Configuração de Logs Estruturados

Configura structlog para emitir logs em formato JSON,
compatível com Amazon CloudWatch Logs (RNF-012).
"""
import logging
import structlog
from app.core.config import settings


def setup_logging() -> None:
    """Configura structlog com processadores para JSON estruturado."""

    # Nível de log baseado na configuração
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Configura o logging padrão do Python
    logging.basicConfig(
        format="%(message)s",
        level=log_level,
    )

    # Configura o structlog para saída JSON
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
