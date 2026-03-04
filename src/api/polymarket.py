from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

import requests


@dataclass(frozen=True)
class PolymarketMarketInfo:
    """Information about a discovered Polymarket market."""
    question: str
    yes_token_id: str
    no_token_id: str
    accepting_orders: bool
    closed: bool
    end_date_iso: str


@dataclass(frozen=True)
class PolymarketQuote:
    token_id: str
    price: float
    bid: float = 0.0
    ask: float = 0.0
    spread: float = 0.0


class PolymarketClient:
    def __init__(self, base_url: str, timeout_seconds: int = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
    
    def find_hourly_bitcoin_market(self, hour_start_et: int, target_date: datetime) -> Optional[PolymarketMarketInfo]:
        """
        Search for the "Bitcoin Up or Down - Hourly" market matching the given hour.
        
        Args:
            hour_start_et: Starting hour in ET (e.g., 2 for "2-3 AM ET")
            target_date: Date to search for
        
        Returns:
            PolymarketMarketInfo with token IDs and market status, or None if not found
        
        Note: Polymarket creates these markets daily. The title format is:
        "Bitcoin Up or Down - Hourly\nMarch 5, 2-3AM ET"
        """
        try:
            response = self.session.get(
                f"{self.base_url}/markets",
                timeout=self.timeout_seconds
            )
            if response.status_code != 200:
                return None
            
            data = response.json()
            markets = data.get('data', [])
            
            # Search for Bitcoin hourly market with matching time
            hour_patterns = [
                f"{hour_start_et}-{hour_start_et+1}AM ET",
                f"{hour_start_et}-{hour_start_et+1} AM ET",
                f"{hour_start_et}AM-{hour_start_et+1}AM ET",
            ]
            
            for market in markets:
                question = market.get('question', '')
                if 'bitcoin' not in question.lower() or 'hourly' not in question.lower():
                    continue
                
                # Check if this matches our hour
                if any(pattern.lower() in question.lower() for pattern in hour_patterns):
                    tokens = market.get('tokens', [])
                    if len(tokens) >= 2:
                        yes_token = next((t for t in tokens if 'yes' in t.get('outcome', '').lower()), None)
                        no_token = next((t for t in tokens if 'no' in t.get('outcome', '').lower()), None)
                        
                        if yes_token and no_token:
                            return PolymarketMarketInfo(
                                question=question,
                                yes_token_id=yes_token['token_id'],
                                no_token_id=no_token['token_id'],
                                accepting_orders=market.get('accepting_orders', False),
                                closed=market.get('closed', True),
                                end_date_iso=market.get('end_date_iso', '')
                            )
            
            return None
        except Exception:
            return None

    def get_token_mid_price(self, token_id: str) -> PolymarketQuote:
        response = self.session.get(
            f"{self.base_url}/book",
            params={"token_id": token_id},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()

        bids = payload.get("bids") or []
        asks = payload.get("asks") or []

        best_bid = float(bids[0]["price"] if bids and isinstance(bids[0], dict) else bids[0][0]) if bids else 0.0
        best_ask = float(asks[0]["price"] if asks and isinstance(asks[0], dict) else asks[0][0]) if asks else 0.0

        if best_bid > 0 and best_ask > 0:
            price = (best_bid + best_ask) / 2.0
            spread = best_ask - best_bid
        elif best_bid > 0:
            price = best_bid
            spread = 0.0
        elif best_ask > 0:
            price = best_ask
            spread = 0.0
        else:
            raise ValueError(f"No usable Polymarket price for token_id={token_id}")

        return PolymarketQuote(
            token_id=token_id, 
            price=price, 
            bid=best_bid, 
            ask=best_ask, 
            spread=spread
        )
