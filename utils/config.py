# utils/config.py
from __future__ import annotations
import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# carrega .env
load_dotenv()

DATA_DIR = Path(os.environ.get("DATA_DIR", "./data_parquet")).resolve()
LOG_DIR  = Path(os.environ.get("LOG_DIR", "./logs")).resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

BINANCE_WS_BASE = "wss://fstream.binance.com/stream"
