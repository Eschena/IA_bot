# utils/logger.py
from loguru import logger
import os, sys
from pathlib import Path

LOG_DIR = Path(os.environ.get("LOG_DIR", "./logs")).resolve()
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger.remove()
logger.add(sys.stdout, level="INFO", colorize=True,
           format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>")
logger.add(LOG_DIR / "collector.log", rotation="10 MB", retention="7 days", level="INFO")
