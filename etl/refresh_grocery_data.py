"""Refresh the local grocery price index from Israel's mandatory supermarket
price-transparency feeds.

This must be run from a network location with an Israeli IP - the chains'
publishing portals block requests from outside Israel. Run it periodically
(e.g. once a day via cron); the Telegram bot itself only ever reads the local
SQLite database this script builds, so the bot process does not need an
Israeli IP.

Usage:
    python -m etl.refresh_grocery_data --chains SHUFERSAL RAMI_LEVY --limit 20
"""

import argparse
import glob
import os

from etl import db
from etl.csv_utils import read_parsed_csv
from etl.text_utils import normalize_text

DUMPS_DIR = "data/dumps"
PARSED_DIR = "data/parsed"
STATUS_DIR = "data/status"


def run_scraper(chains: list[str], limit: int | None) -> None:
    from il_supermarket_scarper import ScarpingTask

    os.makedirs(DUMPS_DIR, exist_ok=True)
    scraper = ScarpingTask(
        enabled_scrapers=chains,
        files_types=["PRICE_FILE", "STORE_FILE"],
        multiprocessing=1,
        output_configuration={"output_mode": "disk", "base_storage_path": DUMPS_DIR},
    )
    scraper.start(limit=limit)
    scraper.join()


def run_parser(chains: list[str], limit: int | None) -> None:
    from il_supermarket_parsers import ConvertingTask

    os.makedirs(PARSED_DIR, exist_ok=True)
    os.makedirs(STATUS_DIR, exist_ok=True)
    task = ConvertingTask(
        source_configuration={"folder": DUMPS_DIR},
        output_configuration={"output_mode": "csv", "output_folder": PARSED_DIR},
        status_configuration={"database_type": "json", "base_path": STATUS_DIR},
        enabled_parsers=chains,
        files_types=["PRICE_FILE", "STORE_FILE"],
        multiprocessing=1,
    )
    task.start(limit=limit)
    task.join()


def _find_csv(file_type: str, chain: str) -> str | None:
    pattern = os.path.join(PARSED_DIR, f"{file_type.lower()}_{chain.lower()}.csv")
    matches = glob.glob(pattern)
    return matches[0] if matches else None


def load_stores(chain: str, db_path: str) -> int:
    path = _find_csv("STORE_FILE", chain)
    if not path:
        print(f"  [stores] no store file found for {chain}, skipping")
        return 0

    df = read_parsed_csv(path)
    rows = []
    for _, row in df.iterrows():
        chain_id = row.get("chainid")
        store_id = row.get("storeid")
        if not chain_id or not store_id:
            continue
        city = row.get("city", "")
        rows.append(
            {
                "chain_id": str(chain_id),
                "store_id": str(store_id),
                "chain_name": row.get("chainname"),
                "store_name": row.get("storename"),
                "address": row.get("address"),
                "city": city,
                "city_norm": normalize_text(city),
            }
        )
    db.upsert_stores(db_path, rows)
    return len(rows)


def load_items(chain: str, db_path: str) -> int:
    path = _find_csv("PRICE_FILE", chain)
    if not path:
        print(f"  [items] no price file found for {chain}, skipping")
        return 0

    df = read_parsed_csv(path)
    rows = []
    for _, row in df.iterrows():
        chain_id = row.get("chainid")
        store_id = row.get("storeid")
        item_code = row.get("itemcode")
        if not chain_id or not store_id or not item_code:
            continue
        try:
            price = float(row.get("itemprice"))
        except (TypeError, ValueError):
            continue
        item_name = row.get("itemname", "")
        rows.append(
            {
                "chain_id": str(chain_id),
                "store_id": str(store_id),
                "item_code": str(item_code),
                "item_name": item_name,
                "item_name_norm": normalize_text(item_name),
                "price": price,
                "unit_of_measure": row.get("unitofmeasure"),
                "updated_at": row.get("priceupdatedate"),
            }
        )
    db.upsert_items(db_path, rows)
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--chains",
        nargs="+",
        default=None,
        help="ScraperFactory/ParserFactory enum names to refresh (default: from GROCERY_CHAINS env var)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max number of files to download/parse per chain (useful for testing)",
    )
    parser.add_argument(
        "--db-path",
        default=None,
        help="Path to the SQLite DB to write to (default: from GROCERY_DB_PATH env var)",
    )
    parser.add_argument(
        "--skip-scrape",
        action="store_true",
        help="Skip downloading and only re-parse+load whatever is already in data/dumps",
    )
    args = parser.parse_args()

    from app.config import config

    chains = args.chains or config.grocery_chains
    db_path = args.db_path or config.grocery_db_path

    db.init_db(db_path)

    if not args.skip_scrape:
        print(f"Scraping chains: {chains}")
        run_scraper(chains, args.limit)

    print(f"Parsing chains: {chains}")
    run_parser(chains, args.limit)

    total_stores = 0
    total_items = 0
    for chain in chains:
        print(f"Loading {chain} into {db_path} ...")
        total_stores += load_stores(chain, db_path)
        total_items += load_items(chain, db_path)

    print(f"Done. Loaded {total_stores} store rows and {total_items} item rows.")


if __name__ == "__main__":
    main()
