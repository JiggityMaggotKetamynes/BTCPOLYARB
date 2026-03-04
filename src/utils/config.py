from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    deribit_base_url: str
    polymarket_base_url: str
    binance_base_url: str
    deribit_expiry: str
    strike_interval: int
    request_timeout_seconds: int
    output_dir: Path
    polymarket_yes_token_id: str | None
    polymarket_no_token_id: str | None


def load_settings() -> Settings:
    load_dotenv()

    return Settings(
        deribit_base_url=os.getenv("DERIBIT_BASE_URL", "https://www.deribit.com/api/v2"),
        polymarket_base_url=os.getenv("POLYMARKET_BASE_URL", "https://clob.polymarket.com"),
        binance_base_url=os.getenv("BINANCE_BASE_URL", "https://api.binance.com"),
        deribit_expiry=os.getenv("DERIBIT_EXPIRY", ""),
        strike_interval=int(os.getenv("STRIKE_INTERVAL", "500")),
        request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "10")),
        output_dir=Path(os.getenv("OUTPUT_DIR", "data/raw")),
        polymarket_yes_token_id=os.getenv("POLYMARKET_YES_TOKEN_ID"),
        polymarket_no_token_id=os.getenv("POLYMARKET_NO_TOKEN_ID"),
    )
