import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from src._internal.configs import ProjectPaths

class VerboseFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(datefmt="%Y-%m-%d %H:%M:%S")
        self.debug_fmt = logging.Formatter(
            "%(asctime)s - [%(levelname)s] - %(name)s - "
            "%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        self.info_fmt = logging.Formatter(
            "%(asctime)s - [%(levelname)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    def format(self, record):
        if record.levelno == logging.DEBUG:
            return self.debug_fmt.format(record)
        else:
            return self.info_fmt.format(record)

class LoggerFactory:
    @staticmethod
    def get_logger(name=__name__, level=logging.INFO) -> logging.Logger:
        logger = logging.getLogger(name)

        if not logger.handlers:
            logger.setLevel(level)
            logger.propagate = False

            formatter = VerboseFormatter()

            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            console_handler.setLevel(level)
            logger.addHandler(console_handler)

            # File handler
            project_paths = ProjectPaths.create()
            log_file = project_paths.logs / "project.log"
            log_file.parent.mkdir(parents=True, exist_ok=True)

            file_handler = TimedRotatingFileHandler(
                filename=log_file,
                when="midnight",
                backupCount=90,
                encoding="utf-8",
                utc=True
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)  # capture more detail in file
            logger.addHandler(file_handler)

            logger.info(f"Logger initialized for {name}. Logs will go to: {log_file}")

        return logger
