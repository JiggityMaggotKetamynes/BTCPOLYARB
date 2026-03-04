from __future__ import annotations

import requests


class BinanceClient:
    def __init__(self, base_url: str, timeout_seconds: int = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()

    def get_live_btc_usdt_price(self) -> float:
        response = self.session.get(
            f"{self.base_url}/api/v3/ticker/price",
            params={"symbol": "BTCUSDT"},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        return float(payload["price"])
