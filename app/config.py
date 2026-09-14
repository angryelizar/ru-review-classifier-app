from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Hugging Face
    hf_token: str | None = Field(default=None, description="HF access token")

    # Model
    model_repo_id: str = "angryelizar/ruBert-base-sentiment-classifier"
    model_max_length: int = 512

    # Dataset
    dataset_repo_id: str = "angryelizar/sentiment_dataset_splitted"
    dataset_config: str | None = Field(default=None, description="Dataset config/subset name, if any")
    dataset_split: str = "test"
    dataset_text_column: str = "text"
    dataset_label_column: str = "label"
    dataset_src_column: str = "src"
    # How many rows to keep in memory after shuffling. 0 = keep the whole split.
    dataset_sample_size: int = 5000

    # Mapping from raw model labels to human-readable names
    label_mapping: dict[str, str] = {
        "LABEL_0": "neutral",
        "LABEL_1": "positive",
        "LABEL_2": "negative",
    }

    # App
    app_title: str = "fsociety // sentiment"
    host: str = "127.0.0.1"
    port: int = 8000


@lru_cache
def get_settings() -> Settings:
    return Settings()
