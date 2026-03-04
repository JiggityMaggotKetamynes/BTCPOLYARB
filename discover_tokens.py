#!/usr/bin/env python3
"""
Pre-discover Polymarket token IDs before the data collection window.

Run this at ~06:00 UTC (1 AM ET) to verify the market exists before
the 07:00-08:00 UTC collection window begins.

Usage:
    python discover_tokens.py --date 2026-03-05
"""
import argparse
from datetime import datetime

from src.api.polymarket import PolymarketClient
from src.utils.config import load_settings


def main():
    parser = argparse.ArgumentParser(description="Discover Polymarket token IDs for a date")
    parser.add_argument(
        "--date",
        type=str,
        required=True,
        help="Target date in YYYY-MM-DD format"
    )
    args = parser.parse_args()
    
    target_date = datetime.strptime(args.date, "%Y-%m-%d")
    settings = load_settings()
    
    print(f"Searching for Polymarket 2-3AM ET market for {target_date.date()}...")
    
    client = PolymarketClient(settings.polymarket_base_url, settings.request_timeout_seconds)
    market = client.find_hourly_bitcoin_market(hour_start_et=2, target_date=target_date)
    
    if not market:
        print("❌ Market not found")
        print("\nPossible reasons:")
        print("  - Market not created yet (usually created a few hours before)")
        print("  - Polymarket changed their naming convention")
        print("  - Date might be too far in the future")
        return 1
    
    print("✓ Market found!\n")
    print(f"Question: {market.question}")
    print(f"End date: {market.end_date_iso}")
    print(f"\nStatus:")
    print(f"  Accepting orders: {market.accepting_orders}")
    print(f"  Closed: {market.closed}")
    print(f"\nToken IDs:")
    print(f"  YES: {market.yes_token_id}")
    print(f"  NO:  {market.no_token_id}")
    
    # Try to get prices
    print(f"\nTesting price fetch...")
    try:
        yes_quote = client.get_token_mid_price(market.yes_token_id)
        no_quote = client.get_token_mid_price(market.no_token_id)
        
        print(f"  YES: ${yes_quote.price:.3f} (bid=${yes_quote.bid:.3f} ask=${yes_quote.ask:.3f} spread={yes_quote.spread:.3f})")
        print(f"  NO:  ${no_quote.price:.3f} (bid=${no_quote.bid:.3f} ask=${no_quote.ask:.3f} spread={no_quote.spread:.3f})")
        
        if yes_quote.spread > 0.1 or no_quote.spread > 0.1:
            print(f"\n⚠️  Wide spreads detected (>10%) - orderbook may be thin")
        
        if not market.accepting_orders:
            print(f"\n⚠️  Market closed for trading - prices may be stale")
    except Exception as e:
        print(f"  ❌ Failed to fetch prices: {e}")
        return 1
    
    print("\n✓ All checks passed - ready for data collection!")
    return 0


if __name__ == "__main__":
    exit(main())
