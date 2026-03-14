import logging
from core.config import LOG_DIR, LOG_LEVEL


LOG_FILE = LOG_DIR / "kindar.log"



def _resolve_log_level():
    return getattr(logging, LOG_LEVEL, logging.INFO)



def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger()
    if logger.handlers:
        return logger

    logger.setLevel(_resolve_log_level())

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(_resolve_log_level())
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(_resolve_log_level())
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Logging initialized. Log file: %s", LOG_FILE)
    return logger



def get_logger(name):
    return logging.getLogger(name)