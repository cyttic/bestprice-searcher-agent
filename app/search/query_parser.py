from app.llm.deepseek_client import chat_json
from app.llm.prompts import QUERY_PARSER_SYSTEM_PROMPT
from app.search.models import Category, ParsedQuery


def parse_query(text: str) -> ParsedQuery:
    data = chat_json(QUERY_PARSER_SYSTEM_PROMPT, text)

    try:
        category = Category(data.get("category", "unknown"))
    except ValueError:
        category = Category.UNKNOWN

    max_price = data.get("max_price")
    try:
        max_price = float(max_price) if max_price is not None else None
    except (TypeError, ValueError):
        max_price = None

    return ParsedQuery(
        product=(data.get("product") or "").strip(),
        city=(data.get("city") or None),
        category=category,
        max_price=max_price,
        notes=(data.get("notes") or None),
        original_text=text,
    )
