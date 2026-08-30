# BestPrice Searcher Agent

A Telegram bot that finds the best price for a product in Israel, filtered by
city. You text it something like:

```
חלב 3% בתל אביב
iPhone 17 128GB בחיפה עד 4000 שקל
```

and it replies with a ranked list of stores/prices.

## How it works

1. **Telegram bot** (`aiogram`, long polling) receives the free-text message.
2. **DeepSeek** (OpenAI-compatible API) parses the message into a structured
   query: product, city, category (grocery vs. general), budget, notes.
3. Depending on category, the query is routed to one of two price sources:
   - **Grocery / supermarket items** → a local SQLite index built from
     Israel's mandatory supermarket price-transparency feeds (the "מחירון"
     data that chains like Shufersal, Rami Levy, Victory, etc. are legally
     required to publish daily). Free, structured, filterable by city/branch.
   - **Everything else** (electronics, general retail, etc.) → a **Tavily**
     web search, with DeepSeek extracting store/price pairs from the search
     results. There is no official price-comparison API for general retail
     in Israel (zap.co.il has no public API and blocks non-Israeli IPs), so
     this path is best-effort rather than a structured database.
4. DeepSeek writes the final human-readable reply.

## Important: the grocery data source needs an Israeli IP

The supermarket chains' price-publishing portals **block requests from
outside Israel**. This only affects the *ETL/refresh* step
(`etl/refresh_grocery_data.py`), which downloads and indexes the data — it
does **not** affect the bot process itself, which only reads the local
SQLite file. In practice this means:

- Run `etl/refresh_grocery_data.py` from a machine with an Israeli IP (a
  home connection in Israel, an Israeli VPS, or behind an Israeli
  proxy/VPN).
- The bot process (`app/main.py`) can run anywhere, since it just queries
  the SQLite DB that script produces.
- If you run everything on one VPS, that VPS needs to be in Israel (or
  reach the internet through an Israeli exit) for the ETL step to work.

This constraint was confirmed while building this project: attempts to
reach the chains' publishing portal from a non-Israeli network resulted in
connection failures.

## Setup

### 1. Create the Telegram bot

1. Open Telegram, message [@BotFather](https://t.me/BotFather).
2. Send `/newbot`, follow the prompts (choose a name and a username ending
   in `bot`).
3. BotFather gives you a token like `123456789:ABC...` — save it.

### 2. Get a Tavily API key (for non-grocery searches)

Sign up at [tavily.com](https://tavily.com) (free tier available) and copy
your API key.

### 3. Install dependencies

Requires Python 3.11 or 3.12 (the supermarket scraper package pins `<3.13`).

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Fill in `.env`:

- `TELEGRAM_BESTPRICE_BOT` — from step 1
- `DEEPSEEK_API_KEY` — your DeepSeek key
- `TAVILY_API_KEY` — from step 2
- `GROCERY_CHAINS` — comma-separated chain codes to index (see
  `ScraperFactory`/`ParserFactory` in
  [israeli-supermarket-scarpers](https://github.com/OpenIsraeliSupermarkets/israeli-supermarket-scarpers)
  for the full list). Defaults to a handful of major chains.

### 5. Build the grocery price index (run from an Israeli IP)

```bash
python -m etl.refresh_grocery_data --limit 20   # small test run first
```

Drop `--limit` for a full run once you've confirmed it works. Re-run this
periodically (e.g. daily via cron) to keep prices fresh — the underlying
feeds update daily:

```cron
0 4 * * * cd /path/to/bestprice-searcher-agent && .venv/bin/python -m etl.refresh_grocery_data
```

If a specific chain's CSV output doesn't have the columns the loader
expects (chains occasionally deviate from the standard schema), check
`data/parsed/*.csv` for that chain and adjust the column lookups in
`etl/refresh_grocery_data.py`.

### 6. Run the bot

```bash
python -m app.main
```

Message your bot on Telegram to test it.

## Project layout

```
app/
  config.py            # env-based settings
  main.py              # bot entrypoint (polling)
  bot/handlers.py       # Telegram message handlers
  llm/                   # DeepSeek client + prompts
  search/
    query_parser.py      # free text -> structured query (via DeepSeek)
    grocery_source.py     # queries the local SQLite grocery index
    general_source.py      # Tavily search + DeepSeek extraction
    router.py               # combines sources, ranks, and summarizes
etl/
  refresh_grocery_data.py   # scrape + parse + load the grocery index
  db.py                      # SQLite schema/helpers
  cities.py                   # Hebrew/English city name normalization
data/
  grocery.db                  # built by the ETL script (gitignored)
```

## Known limitations / next steps

- The grocery index currently covers only the chains listed in
  `GROCERY_CHAINS`. Add more `ScraperFactory` names to widen coverage; more
  chains means a longer ETL run.
- City matching for groceries is exact-match on a normalized city string,
  with a small alias table (`etl/cities.py`) for common English spellings.
  Extend that table if users type city names it doesn't recognize.
- The general-goods path depends entirely on what DeepSeek can extract from
  web search snippets — it's best-effort, not a verified price feed. Treat
  it as a fallback, not a guarantee.
- No conversation memory: each message is treated independently. Adding
  multi-turn refinement ("cheaper?", "only that store") would need session
  state per Telegram chat.
