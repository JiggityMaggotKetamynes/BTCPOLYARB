from __future__ import annotations

import argparse
from datetime import datetime, timezone

from src.collector.data_collector import collect_day
from src.utils.config import load_settings


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect 07:00-08:00 UTC BTCPOLYARB data")
    parser.add_argument(
        "--date",
        type=str,
        default=datetime.now(timezone.utc).date().isoformat(),
        help="UTC date in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use generated mock prices instead of live API calls",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    settings = load_settings()

    output_file = collect_day(target_date=target_date, settings=settings, mock=args.mock)
    print(f"Collected data written to: {output_file}")


if __name__ == "__main__":
    main()
