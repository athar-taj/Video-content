import sys
from loguru import logger
from shared.config.settings import settings

def setup_logging():
    # Remove default handler
    logger.remove()
    
    # Add structured stdout handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG" if settings.DEBUG else "INFO",
        colorize=True
    )
    
    # Add file handler for errors
    logger.add(
        "logs/error.log",
        rotation="10 MB",
        retention="10 days",
        level="ERROR",
        compression="zip"
    )

    return logger

# Initialize logger
log = setup_logging()
