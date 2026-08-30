"""Normalization of Israeli city names so a user typing in English/Hebrew,
with or without nikud/prefixes, still matches how chains spell the city in
their store XML files.
"""

# English/transliterated -> canonical Hebrew spelling used by most chains.
CITY_ALIASES: dict[str, str] = {
    "tel aviv": "תל אביב",
    "tel-aviv": "תל אביב",
    "telaviv": "תל אביב",
    "jerusalem": "ירושלים",
    "haifa": "חיפה",
    "beer sheva": "באר שבע",
    "beersheba": "באר שבע",
    "petah tikva": "פתח תקווה",
    "petach tikva": "פתח תקווה",
    "rishon lezion": "ראשון לציון",
    "rishon le zion": "ראשון לציון",
    "netanya": "נתניה",
    "holon": "חולון",
    "bnei brak": "בני ברק",
    "ramat gan": "רמת גן",
    "ashdod": "אשדוד",
    "ashkelon": "אשקלון",
    "rehovot": "רחובות",
    "bat yam": "בת ים",
    "herzliya": "הרצליה",
    "kfar saba": "כפר סבא",
    "raanana": "רעננה",
    "ra'anana": "רעננה",
    "modiin": "מודיעין",
    "modi'in": "מודיעין",
    "eilat": "אילת",
    "tiberias": "טבריה",
    "nazareth": "נצרת",
    "acre": "עכו",
    "akko": "עכו",
    "kiryat gat": "קרית גת",
    "kiryat ata": "קרית אתא",
}


def normalize_city(city: str) -> str:
    """Return a canonical Hebrew city name for matching, best-effort."""
    key = city.strip().lower()
    if key in CITY_ALIASES:
        return CITY_ALIASES[key]
    # Already Hebrew (or unknown) - strip common prefixes/whitespace only.
    return city.strip()
