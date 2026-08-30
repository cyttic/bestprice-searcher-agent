import os

from rapidfuzz import fuzz

from app.config import config
from app.search.models import PriceResult
from etl import db
from etl.cities import normalize_city
from etl.text_utils import normalize_text

MATCH_THRESHOLD = 60


def search_grocery(product: str, city: str | None, limit: int = 10) -> list[PriceResult]:
    if not product or not os.path.exists(config.grocery_db_path):
        return []

    product_norm = normalize_text(product)
    tokens = product_norm.split()
    if not tokens:
        return []

    like_clauses = " AND ".join(["items.item_name_norm LIKE ?"] * len(tokens))
    like_params = [f"%{t}%" for t in tokens]

    query = f"""
        SELECT items.item_name, items.price, items.unit_of_measure,
               stores.store_name, stores.chain_name, stores.city
        FROM items
        JOIN stores ON items.chain_id = stores.chain_id AND items.store_id = stores.store_id
        WHERE {like_clauses}
    """
    params = list(like_params)

    if city:
        city_norm = normalize_text(normalize_city(city))
        query += " AND stores.city_norm = ?"
        params.append(city_norm)

    query += " ORDER BY items.price ASC LIMIT 500"

    with db.connect(config.grocery_db_path) as conn:
        rows = conn.execute(query, params).fetchall()

    results = []
    seen_stores = set()
    for row in rows:
        score = fuzz.token_set_ratio(product_norm, normalize_text(row["item_name"]))
        if score < MATCH_THRESHOLD:
            continue
        store_key = (row["store_name"], row["city"])
        if store_key in seen_stores:
            continue
        seen_stores.add(store_key)
        results.append(
            PriceResult(
                item_name=row["item_name"],
                price=row["price"],
                currency="ILS",
                store_name=f"{row['chain_name']} - {row['store_name']}"
                if row["chain_name"]
                else row["store_name"],
                city=row["city"],
                source="grocery",
            )
        )
        if len(results) >= limit:
            break

    return results
