from dataclasses import dataclass
from enum import Enum


class Category(str, Enum):
    GROCERY = "grocery"
    GENERAL = "general"
    UNKNOWN = "unknown"


@dataclass
class ParsedQuery:
    product: str
    city: str | None
    category: Category
    max_price: float | None
    notes: str | None
    original_text: str


@dataclass
class PriceResult:
    item_name: str
    price: float
    currency: str
    store_name: str
    city: str | None
    source: str  # "grocery" or "web"
    url: str | None = None
