import logging
import sys
from typing import Optional

class LoggerService:
    _instance: Optional['LoggerService'] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerService, cls).__new__(cls)
            cls._setup_logger()
        return cls._instance

    @classmethod
    def _setup_logger(cls):
        # Create logger
        cls._logger = logging.getLogger('app')
        cls._logger.setLevel(logging.INFO)

        # Create console handler with formatting
        console_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        cls._logger.addHandler(console_handler)

    @classmethod
    def info(cls, message: str):
        if cls._logger is None:
            cls._setup_logger()
        cls._logger.info(message)

    @classmethod
    def error(cls, message: str):
        if cls._logger is None:
            cls._setup_logger()
        cls._logger.error(message)

    @classmethod
    def warning(cls, message: str):
        if cls._logger is None:
            cls._setup_logger()
        cls._logger.warning(message)

    @classmethod
    def debug(cls, message: str):
        if cls._logger is None:
            cls._setup_logger()
        cls._logger.debug(message)

logger = LoggerService() 