import os, sys
from loguru import logger


def setup_logging():
    """Configures Loguru to handle all application logs."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Remove default handler
    logger.remove()

    # Add a custom handler with the format you were seeing
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level=log_level,
        enqueue=True  # Keeps the logger from blocking the main scan logic
    )

    logger.info(f"📜 Logger initialized at level: {log_level}")
    return logger


# Initialize the global logger
log = setup_logging()