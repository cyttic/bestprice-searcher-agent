"""Online store URLs for supermarket chains, keyed by the same ScraperFactory
/ ParserFactory enum name used in GROCERY_CHAINS. The government price feeds
carry no product-page URLs (they only describe physical branch prices), so
this is the best "where can I buy it" link we can offer for grocery results:
the chain's own online store homepage.

Only add an entry once you've verified the domain actually belongs to that
chain - a wrong link is worse than no link.
"""

CHAIN_WEBSITES: dict[str, str] = {
    "SHUFERSAL": "https://www.shufersal.co.il",
    "RAMI_LEVY": "https://www.rami-levy.co.il",
    "VICTORY_NEW_SOURCE": "https://www.victoryonline.co.il",
    "VICTORY": "https://www.victoryonline.co.il",
    "YOHANANOF": "https://yochananof.co.il",
    "OSHER_AD": "https://osherad.co.il",
}


def get_chain_url(chain_code: str | None) -> str | None:
    if not chain_code:
        return None
    return CHAIN_WEBSITES.get(chain_code.upper())
