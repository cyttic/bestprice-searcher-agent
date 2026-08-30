import requests

from app.config import config
from app.llm.deepseek_client import chat_json
from app.llm.prompts import WEB_EXTRACTION_SYSTEM_PROMPT
from app.search.models import PriceResult

TAVILY_URL = "https://api.tavily.com/search"


def _web_search(query: str, max_results: int = 8) -> list[dict]:
    response = requests.post(
        TAVILY_URL,
        json={
            "api_key": config.tavily_api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
            "include_answer": False,
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json().get("results", [])


def search_general(product: str, city: str | None, limit: int = 8) -> list[PriceResult]:
    if not product or not config.tavily_api_key:
        return []

    location = f" ב{city}" if city else ""
    query = f"מחיר {product}{location} קניה בישראל"

    try:
        web_results = _web_search(query, max_results=limit)
    except requests.RequestException:
        return []

    if not web_results:
        return []

    excerpt_lines = []
    for r in web_results:
        excerpt_lines.append(
            f"- title: {r.get('title')}\n  url: {r.get('url')}\n  content: {r.get('content', '')[:500]}"
        )
    user_prompt = f"Product query: {product}\nCity: {city or 'any'}\n\nSearch results:\n" + "\n".join(excerpt_lines)

    try:
        extracted = chat_json(WEB_EXTRACTION_SYSTEM_PROMPT, user_prompt)
    except (ValueError, KeyError):
        return []

    results = []
    for item in extracted.get("results", [])[:limit]:
        try:
            price = float(item.get("price"))
        except (TypeError, ValueError):
            continue
        results.append(
            PriceResult(
                item_name=item.get("item_name", product),
                price=price,
                currency="ILS",
                store_name=item.get("store_name", "unknown"),
                city=item.get("city"),
                source="web",
                url=item.get("url"),
            )
        )

    results.sort(key=lambda r: r.price)
    return results
