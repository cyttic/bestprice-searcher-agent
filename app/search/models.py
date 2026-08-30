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
    # Whether the presence of a physical branch in `city` is actually backed
    # by evidence (an address/branch mention), as opposed to just being where
    # the user asked to search. Grocery data comes from real per-branch
    # records, so it's always verified; web results default to unverified
    # until the extraction step confirms a branch.
    location_verified: bool = True
