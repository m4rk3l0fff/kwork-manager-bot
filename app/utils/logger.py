from loguru import logger
from sys import stdout
from os import makedirs


def setup_logger():
    makedirs('logs', exist_ok=True)

    logger.remove()
    logger.add(
        stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}",
        level="INFO"
    )
    logger.add(
        "logs/app.log",
        rotation="10 MB",  # новый файл каждые 10мб
        retention="7 days",  # хранить 7 дней
        compression="zip",  # сжимать старые
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="DEBUG"
    )

    return logger
