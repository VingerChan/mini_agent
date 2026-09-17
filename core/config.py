from __future__ import annotations

from dataclasses import dataclass

from dotenv import load_dotenv
import os


@dataclass(frozen=True)
class Settings:
    dashscope_api_key: str
    dashscope_base_url: str
    model: str


def _load_settings() -> Settings:
    load_dotenv(override=True)
    return Settings(
        dashscope_api_key=os.getenv("DASHSCOPE_API_KEY", ""),
        dashscope_base_url=os.getenv("DASHSCOPE_BASE_URL", ""),
        model=os.getenv("MODEL", "qwen-max"),
    )


settings: Settings = _load_settings()
