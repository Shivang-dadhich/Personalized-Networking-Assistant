from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache


@dataclass(slots=True)
class Settings:
	app_name: str = "Personalized Networking Assistant"
	api_prefix: str = "/api"
	allow_origins: tuple[str, ...] = ("*",)
	distilbert_model_name: str = "distilbert-base-uncased"
	gpt2_model_name: str = "gpt2"
	wikipedia_language: str = "en"
	wikipedia_user_agent: str = "personalized-networking-assistant/0.1.0"
	max_history_items: int = 100


@lru_cache(maxsize=1)
def get_settings() -> Settings:
	return Settings()


settings = get_settings()

