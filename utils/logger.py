"""Logger module"""

from loguru import logger

logger.add("log.log", level="DEBUG", format="{name} {message}")
