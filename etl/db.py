import sqlite3
from contextlib import contextmanager

SCHEMA = """
CREATE TABLE IF NOT EXISTS stores (
    chain_id TEXT NOT NULL,
    store_id TEXT NOT NULL,
    chain_name TEXT,
    store_name TEXT,
    address TEXT,
    city TEXT,
    city_norm TEXT,
    PRIMARY KEY (chain_id, store_id)
);

CREATE TABLE IF NOT EXISTS items (
    chain_id TEXT NOT NULL,
    store_id TEXT NOT NULL,
    item_code TEXT NOT NULL,
    item_name TEXT,
    item_name_norm TEXT,
    price REAL,
    unit_of_measure TEXT,
    updated_at TEXT,
    PRIMARY KEY (chain_id, store_id, item_code)
);

CREATE INDEX IF NOT EXISTS idx_items_name_norm ON items(item_name_norm);
CREATE INDEX IF NOT EXISTS idx_stores_city_norm ON stores(city_norm);
"""


@contextmanager
def connect(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path: str) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.commit()


def upsert_stores(db_path: str, rows: list[dict]) -> None:
    if not rows:
        return
    with connect(db_path) as conn:
        conn.executemany(
            """
            INSERT INTO stores (chain_id, store_id, chain_name, store_name, address, city, city_norm)
            VALUES (:chain_id, :store_id, :chain_name, :store_name, :address, :city, :city_norm)
            ON CONFLICT(chain_id, store_id) DO UPDATE SET
                chain_name=excluded.chain_name,
                store_name=excluded.store_name,
                address=excluded.address,
                city=excluded.city,
                city_norm=excluded.city_norm
            """,
            rows,
        )
        conn.commit()


def upsert_items(db_path: str, rows: list[dict]) -> None:
    if not rows:
        return
    with connect(db_path) as conn:
        conn.executemany(
            """
            INSERT INTO items (chain_id, store_id, item_code, item_name, item_name_norm, price, unit_of_measure, updated_at)
            VALUES (:chain_id, :store_id, :item_code, :item_name, :item_name_norm, :price, :unit_of_measure, :updated_at)
            ON CONFLICT(chain_id, store_id, item_code) DO UPDATE SET
                item_name=excluded.item_name,
                item_name_norm=excluded.item_name_norm,
                price=excluded.price,
                unit_of_measure=excluded.unit_of_measure,
                updated_at=excluded.updated_at
            """,
            rows,
        )
        conn.commit()
