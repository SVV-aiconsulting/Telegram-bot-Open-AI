import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Config:
    bot_token: str
    openai_api_key: str
    api_base_url: str = "https://api.openai.com/v1"
    proxy_url: str | None = None


def load_config() -> Config:
    bot_token = os.getenv("BOT_TOKEN")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    api_base_url = os.getenv("API_BASE_URL", "https://api.openai.com/v1").strip()
    proxy_url = os.getenv("PROXY_URL", "").strip() or None

    if not bot_token:
        raise RuntimeError("BOT_TOKEN is not set. Add it to .env")
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Add it to .env")
    if not api_base_url:
        api_base_url = "https://api.openai.com/v1"

    return Config(
        bot_token=bot_token,
        openai_api_key=openai_api_key,
        api_base_url=api_base_url.rstrip("/"),
        proxy_url=proxy_url,
    )
