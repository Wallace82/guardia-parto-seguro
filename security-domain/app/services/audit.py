import structlog
import logging

def configure_audit_logging():
    """
    Configura o structlog para gerar logs em formato JSON.
    Estes logs devem ser irrefutáveis e preparados para envio ao Amazon CloudWatch Logs.
    """
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.AsyncBoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Redireciona logs padrão do Python para o structlog
    logging.basicConfig(
        format="%(message)s",
        stream=None,
        level=logging.INFO,
    )
