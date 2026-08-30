from app.llm.deepseek_client import chat_text
from app.llm.prompts import RESULT_SUMMARY_SYSTEM_PROMPT
from app.search.general_source import search_general
from app.search.grocery_source import search_grocery
from app.search.models import Category, ParsedQuery, PriceResult
from app.search.query_parser import parse_query


def find_prices(parsed: ParsedQuery) -> list[PriceResult]:
    if not parsed.product:
        return []

    results: list[PriceResult] = []

    if parsed.category in (Category.GROCERY, Category.UNKNOWN):
        results = search_grocery(parsed.product, parsed.city)

    if not results:
        results = search_general(parsed.product, parsed.city)

    if parsed.max_price is not None:
        results = [r for r in results if r.price <= parsed.max_price]

    results.sort(key=lambda r: r.price)
    return results


def handle_message(text: str) -> str:
    parsed = parse_query(text)

    if not parsed.product:
        return "לא הצלחתי להבין איזה מוצר אתה מחפש. נסה לנסח מחדש, למשל: \"חלב 3% בתל אביב\"."

    results = find_prices(parsed)

    lines = []
    for r in results:
        location = f", {r.city}" if r.city else ""
        link_note = f" [{r.url}]" if r.url else ""
        lines.append(f"{r.store_name}{location}: ₪{r.price:.2f}{link_note}")

    user_prompt = (
        f"User's original message: {text}\n"
        f"Parsed product: {parsed.product}\n"
        f"City filter: {parsed.city or 'none'}\n\n"
        f"Results:\n" + ("\n".join(lines) if lines else "(no results found)")
    )

    return chat_text(RESULT_SUMMARY_SYSTEM_PROMPT, user_prompt)
