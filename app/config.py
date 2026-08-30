import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _split_csv(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


@dataclass(frozen=True)
class Config:
    telegram_bot_token: str = os.environ.get("TELEGRAM_BESTPRICE_BOT", "")

    deepseek_api_key: str = os.environ.get("DEEPSEEK_API_KEY", "")
    deepseek_base_url: str = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    deepseek_model: str = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")

    tavily_api_key: str = os.environ.get("TAVILY_API_KEY", "")

    grocery_db_path: str = os.environ.get("GROCERY_DB_PATH", "data/grocery.db")
    grocery_chains: list[str] = field(
        default_factory=lambda: _split_csv(
            os.environ.get("GROCERY_CHAINS", "SHUFERSAL,RAMI_LEVY,VICTORY_NEW_SOURCE,YOHANANOF,OSHER_AD")
        )
    )

    def validate(self) -> None:
        missing = []
        if not self.telegram_bot_token:
            missing.append("TELEGRAM_BESTPRICE_BOT")
        if not self.deepseek_api_key:
            missing.append("DEEPSEEK_API_KEY")
        if missing:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")


config = Config()
