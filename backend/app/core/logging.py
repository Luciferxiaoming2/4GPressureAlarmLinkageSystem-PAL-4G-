import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import settings


def _build_log_paths() -> tuple[Path, Path]:
    today = datetime.now().strftime("%Y-%m-%d")
    daily_dir = settings.log_root_path / today
    error_dir = settings.log_root_path / "errors" / today
    daily_dir.mkdir(parents=True, exist_ok=True)
    error_dir.mkdir(parents=True, exist_ok=True)
    return daily_dir / "app.log", error_dir / "error.log"


def configure_logging() -> None:
    app_log_path, error_log_path = _build_log_paths()
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 避免在测试或热重载时重复叠加相同 handler。
    if getattr(root_logger, "_pal_4g_logging_configured", False):
        return

    app_handler = RotatingFileHandler(
        app_log_path,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    app_handler.setLevel(log_level)
    app_handler.setFormatter(formatter)

    error_handler = RotatingFileHandler(
        error_log_path,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    root_logger._pal_4g_logging_configured = True

    logging.getLogger(__name__).info(
        "日志系统已初始化，普通日志目录: %s，错误日志目录: %s",
        app_log_path.parent,
        error_log_path.parent,
    )
