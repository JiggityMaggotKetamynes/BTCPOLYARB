from __future__ import annotations

import csv
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
import random
from typing import Any

from src.api.deribit import DeribitClient
from src.api.polymarket import PolymarketClient
from src.utils.config import Settings


def _minute_range_0700_to_0800_utc(target_date: date) -> list[datetime]:
    start_dt = datetime.combine(target_date, time(7, 0), tzinfo=timezone.utc)
    return [start_dt + timedelta(minutes=index) for index in range(61)]


def _write_rows(output_file: Path, rows: list[dict[str, Any]]) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return

    field_names = list(rows[0].keys())
    with output_file.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(rows)


def collect_day(target_date: date, settings: Settings, mock: bool = False) -> Path:
    output_file = settings.output_dir / f"{target_date.isoformat()}.csv"
    minute_marks = _minute_range_0700_to_0800_utc(target_date)

    deribit = DeribitClient(settings.deribit_base_url, settings.request_timeout_seconds)

    if mock:
        p = 65000.0
    else:
        p = deribit.get_hour_open(minute_marks[0])

    call_sell_strike, put_sell_strike = deribit.nearest_strikes_from_reference(
        p, settings.strike_interval
    )
    call_buy_strike = call_sell_strike - settings.strike_interval
    put_buy_strike = put_sell_strike + settings.strike_interval

    call_sell_instrument = deribit.build_option_instrument(
        settings.deribit_expiry, call_sell_strike, "C"
    )
    call_buy_instrument = deribit.build_option_instrument(
        settings.deribit_expiry, call_buy_strike, "C"
    )
    put_sell_instrument = deribit.build_option_instrument(
        settings.deribit_expiry, put_sell_strike, "P"
    )
    put_buy_instrument = deribit.build_option_instrument(
        settings.deribit_expiry, put_buy_strike, "P"
    )

    polymarket = PolymarketClient(
        settings.polymarket_base_url, settings.request_timeout_seconds
    )
    
    # Find Polymarket token IDs for today's 2-3 AM ET market (07:00-08:00 UTC)
    pm_market = None
    if not mock:
        pm_market = polymarket.find_hourly_bitcoin_market(hour_start_et=2, target_date=target_date)
        if not pm_market:
            print(f"[WARN] Could not find Polymarket 2-3 AM ET market for {target_date}. Using mock PM prices.")
        else:
            print(f"[INFO] Found Polymarket market: {pm_market.question[:60]}...")
            print(f"[INFO]   Status: accepting_orders={pm_market.accepting_orders}, closed={pm_market.closed}")
            if pm_market.closed:
                print(f"[INFO]   Market is closed - prices may be stale or have wide spreads")
            if not pm_market.accepting_orders:
                print(f"[INFO]   Market not accepting orders - orderbook reflects pre-closure state")

    # Debug prints for Deribit instruments and strikes
    print(f"[DEBUG] deribit_expiry: {settings.deribit_expiry}")
    print(f"[DEBUG] call_sell_instrument: {call_sell_instrument}")
    print(f"[DEBUG] call_buy_instrument: {call_buy_instrument}")
    print(f"[DEBUG] put_sell_instrument: {put_sell_instrument}")
    print(f"[DEBUG] put_buy_instrument: {put_buy_instrument}")
    print(f"[DEBUG] call_sell_strike: {call_sell_strike}, call_buy_strike: {call_buy_strike}")
    print(f"[DEBUG] put_sell_strike: {put_sell_strike}, put_buy_strike: {put_buy_strike}")
    rows: list[dict[str, Any]] = []
    for minute_mark in minute_marks:
        if mock:
            price_live = p + random.uniform(-250, 250)
            call_sell_price = random.uniform(0.05, 0.45)
            call_buy_price = max(0.01, call_sell_price - random.uniform(0.01, 0.15))
            put_sell_price = random.uniform(0.05, 0.45)
            put_buy_price = max(0.01, put_sell_price - random.uniform(0.01, 0.15))
            yes_price = random.uniform(0.3, 0.7)
            no_price = 1.0 - yes_price
        else:
            if not settings.deribit_expiry:
                raise ValueError("DERIBIT_EXPIRY is required when mock=False")

            # Debug prints before first Deribit API call
            print(f"[DEBUG] About to call Deribit API with:")
            print(f"  call_sell_instrument: {call_sell_instrument}")
            print(f"  call_buy_instrument: {call_buy_instrument}")
            print(f"  put_sell_instrument: {put_sell_instrument}")
            print(f"  put_buy_instrument: {put_buy_instrument}")

            price_live = deribit.get_live_btc_price()
            call_sell_price = deribit.get_option_mid_price(call_sell_instrument).price
            call_buy_price = deribit.get_option_mid_price(call_buy_instrument).price
            put_sell_price = deribit.get_option_mid_price(put_sell_instrument).price
            put_buy_price = deribit.get_option_mid_price(put_buy_instrument).price

            # Use discovered tokens or fallback to 0.5/0.5
            if pm_market:
                try:
                    yes_quote = polymarket.get_token_mid_price(pm_market.yes_token_id)
                    no_quote = polymarket.get_token_mid_price(pm_market.no_token_id)
                    yes_price = yes_quote.price
                    no_price = no_quote.price
                    
                    # Log wide spreads as potential data quality issues
                    if yes_quote.spread > 0.1:  # 10% spread
                        print(f"[WARN] Wide YES spread at {minute_mark}: bid={yes_quote.bid:.3f} ask={yes_quote.ask:.3f} (spread={yes_quote.spread:.3f})")
                    if no_quote.spread > 0.1:
                        print(f"[WARN] Wide NO spread at {minute_mark}: bid={no_quote.bid:.3f} ask={no_quote.ask:.3f} (spread={no_quote.spread:.3f})")
                except Exception as e:
                    print(f"[WARN] Failed to get Polymarket prices at {minute_mark}: {e}")
                    yes_price = 0.5
                    no_price = 0.5
            else:
                yes_price = 0.5
                no_price = 0.5

        rows.append(
            {
                "timestamp_utc": minute_mark.isoformat(),
                "p": round(p, 6),
                "price_live": round(price_live, 6),
                "call_sell_strike": call_sell_strike,
                "call_buy_strike": call_buy_strike,
                "put_sell_strike": put_sell_strike,
                "put_buy_strike": put_buy_strike,
                "call_sell_price": round(call_sell_price, 8),
                "call_buy_price": round(call_buy_price, 8),
                "call_net_cost": round(call_buy_price - call_sell_price, 8),
                "put_sell_price": round(put_sell_price, 8),
                "put_buy_price": round(put_buy_price, 8),
                "put_net_cost": round(put_buy_price - put_sell_price, 8),
                "yes_price": round(yes_price, 8),
                "no_price": round(no_price, 8),
            }
        )

    _write_rows(output_file, rows)
    return output_file
