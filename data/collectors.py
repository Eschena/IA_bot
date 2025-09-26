# data/collectors.py
from __future__ import annotations
import asyncio, json, time
from typing import Iterable
import websockets
from utils.config import BINANCE_WS_BASE
from utils.logger import logger
from data.storage import ParquetRotatingWriter

def build_stream_url(symbols: Iterable[str]) -> str:
    """
    Monta a URL de stream combinada da Binance Futures USDⓈ-M.
    Inclui: bookTicker, depth10@100ms, aggTrade e !forceOrder@arr (global).
    """
    sl = [s.lower() for s in symbols]
    parts = []
    for s in sl:
        parts += [f"{s}@bookTicker", f"{s}@depth10@100ms", f"{s}@aggTrade"]
    parts += ["!forceOrder@arr"]  # liquidações globais
    streams = "/".join(parts)
    return f"{BINANCE_WS_BASE}?streams={streams}"

def route_symbol(msg: dict) -> str | None:
    """
    Deduz o símbolo da mensagem (para rotear arquivo de saída).
    Retorna 'GLOBAL' quando for o stream de liquidações (!forceOrder@arr).
    """
    stream = msg.get("stream", "")
    if stream == "!forceOrder@arr":
        return "GLOBAL"
    return stream.split("@")[0].upper() if "@" in stream else None

async def run_collector(symbols: list[str]):
    url = build_stream_url(symbols)
    logger.info(f"[ws] connecting: {url}")

    writers = {sym.upper(): ParquetRotatingWriter(sym, "ws") for sym in symbols}
    writers["GLOBAL"] = ParquetRotatingWriter("GLOBAL", "forceOrders")

    backoff = 1.0
    while True:
        try:
            async with websockets.connect(url, ping_interval=20, ping_timeout=20, max_queue=10_000) as ws:
                logger.info("[ws] connected")
                backoff = 1.0
                async for raw in ws:
                    now = time.time()
                    try:
                        j = json.loads(raw)
                        j["ts_recv"] = now
                        sym = route_symbol(j) or "GLOBAL"
                        out = {
                            "stream": j.get("stream"),
                            "ts_recv": now,
                            "data": j.get("data"),
                        }
                        writers.setdefault(sym, ParquetRotatingWriter(sym, "ws")).add(out)
                    except Exception as e:
                        logger.warning(f"[ws] parse error: {e}")
        except Exception as e:
            logger.error(f"[ws] disconnected: {e}; reconnecting in {backoff:.1f}s")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 30.0)

def main():
    import argparse
    p = argparse.ArgumentParser(description="Binance Futures WS collector (bookTicker, depth, aggTrade, forceOrder)")
    p.add_argument("--symbols", required=True, help="Lista separada por vírgula. Ex.: BTCUSDT,ETHUSDT")
    p.add_argument("--duration", type=int, default=0, help="Duração em segundos (0 = infinito)")
    args = p.parse_args()
    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    if not symbols:
        raise SystemExit("Nenhum símbolo válido.")
    loop = asyncio.get_event_loop()
    task = loop.create_task(run_collector(symbols))
    if args.duration > 0:
        loop.call_later(args.duration, task.cancel)
    try:
        loop.run_until_complete(task)
    except asyncio.CancelledError:
        logger.info("[ws] stopped by duration")

if __name__ == "__main__":
    main()
