from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import math

import requests


@dataclass(frozen=True)
class DeribitQuote:
    instrument_name: str
    price: float


class DeribitClient:

        def get_nearest_btc_option_expiry(self, today: datetime) -> str:
            """
            Fetch all BTC option instruments, extract expiry codes, and return the soonest expiry after today.
            """
            result = self._get("/public/get_instruments", {"currency": "BTC", "kind": "option"})
            expiries = set()
            for inst in result:
                name = inst.get("instrument_name", "")
                # Example: BTC-07MAR26-70000-C
                parts = name.split("-")
                if len(parts) >= 3:
                    expiries.add(parts[1])
            # Convert expiry codes to datetime for comparison
            def expiry_to_dt(code):
                # e.g., 07MAR26 -> 2026-03-07
                try:
                    return datetime.strptime(code, "%d%b%y")
                except Exception:
                    return None
            expiry_dates = sorted([expiry_to_dt(e) for e in expiries if expiry_to_dt(e)], key=lambda d: d)
            for dt in expiry_dates:
                if dt and dt.date() >= today.date():
                    return dt.strftime("%d%b%y").upper()
            # fallback: return soonest expiry if none are after today
            if expiry_dates:
                return expiry_dates[0].strftime("%d%b%y").upper()
            raise ValueError("No BTC option expiries found on Deribit")
    def __init__(self, base_url: str, timeout_seconds: int = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()

    def _get(self, path: str, params: dict) -> dict:
        response = self.session.get(
            f"{self.base_url}{path}", params=params, timeout=self.timeout_seconds
        )
        response.raise_for_status()
        payload = response.json()
        if "result" not in payload:
            raise ValueError(f"Unexpected Deribit response: {payload}")
        return payload["result"]

    def get_hour_open(self, hour_start_utc: datetime) -> float:
        if hour_start_utc.tzinfo is None:
            raise ValueError("hour_start_utc must be timezone-aware UTC datetime")

        start_ms = int(hour_start_utc.timestamp() * 1000)
        end_ms = int((hour_start_utc + timedelta(hours=1)).timestamp() * 1000)

        result = self._get(
            "/public/get_tradingview_chart_data",
            {
                "instrument_name": "BTC-PERPETUAL",
                "start_timestamp": start_ms,
                "end_timestamp": end_ms,
                "resolution": "60",
            },
        )

        open_values = result.get("open") or []
        if not open_values:
            raise ValueError("No Deribit hour open data returned")
        return float(open_values[0])

    def get_live_btc_price(self) -> float:
        result = self._get(
            "/public/ticker",
            {
                "instrument_name": "BTC-PERPETUAL",
            },
        )
        return float(result["last_price"])

    @staticmethod
    def nearest_strikes_from_reference(reference_price: float, interval: int = 500) -> tuple[int, int]:
        sell_call_strike = int(math.floor(reference_price / interval) * interval)
        sell_put_strike = int(math.ceil(reference_price / interval) * interval)
        return sell_call_strike, sell_put_strike

    @staticmethod
    def build_option_instrument(expiry: str, strike: int, option_type: str) -> str:
        option_type = option_type.upper()
        if option_type not in {"C", "P"}:
            raise ValueError("option_type must be 'C' or 'P'")
        return f"BTC-{expiry}-{strike}-{option_type}"

    def get_option_mid_price(self, instrument_name: str) -> DeribitQuote:
        result = self._get(
            "/public/ticker",
            {
                "instrument_name": instrument_name,
            },
        )

        best_bid = float(result.get("best_bid_price") or 0)
        best_ask = float(result.get("best_ask_price") or 0)

        if best_bid > 0 and best_ask > 0:
            price = (best_bid + best_ask) / 2.0
        elif result.get("mark_price") is not None:
            price = float(result["mark_price"])
        elif result.get("last_price") is not None:
            price = float(result["last_price"])
        else:
            raise ValueError(f"No usable Deribit price for {instrument_name}")

        return DeribitQuote(instrument_name=instrument_name, price=price)
