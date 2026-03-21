from loguru import logger
from sys import stdout
from os import makedirs


def setup_logger():
    makedirs('logs', exist_ok=True)

    logger.remove()

    logger.add(
        stdout,
        format="<green>{time:HH:mm:ss}</green> | "
               "<level>{level: <7}</level> | "
               "<cyan>{name}</cyan> | "
               "{message}",
        level="INFO"
    )

    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | "
               "{level: <7} | "
               "{name} | "
               "{message}",
        level="DEBUG"
    )

    return logger
