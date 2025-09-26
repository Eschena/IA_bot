# data/storage.py
from __future__ import annotations
import time
from pathlib import Path
import pandas as pd
from utils.config import DATA_DIR
from utils.logger import logger

class ParquetRotatingWriter:
    """
    Junta eventos em memória e grava em parquet a cada N registros ou N segundos.
    """
    def __init__(self, symbol: str, suffix: str = "raw", max_rows: int = 5_000, max_secs: int = 30):
        self.symbol = symbol.upper()
        self.suffix = suffix
        self.max_rows = max_rows
        self.max_secs = max_secs
        self._rows: list[dict] = []
        self._t0 = time.time()
        self.out_dir = DATA_DIR / "raw" / self.symbol
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def add(self, row: dict):
        self._rows.append(row)
        now = time.time()
        if len(self._rows) >= self.max_rows or (now - self._t0) >= self.max_secs:
            self.flush()

    def flush(self):
        if not self._rows:
            return
        ts = int(time.time())
        path = self.out_dir / f"{self.suffix}_{ts}.parquet"
        df = pd.DataFrame(self._rows)
        df.to_parquet(path, index=False)
        logger.info(f"[write] {self.symbol}: wrote {len(df)} rows → {path.name}")
        self._rows.clear()
        self._t0 = time.time()
