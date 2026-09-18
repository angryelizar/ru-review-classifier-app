from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    model_repo_id: str = "angryelizar/ruBert-base-sentiment-classifier-final"
    model_max_length: int = 267

    dataset_repo_id: str = "angryelizar/sentiment_dataset_splitted"
    dataset_config: str | None = None
    dataset_split: str = "test"
    dataset_text_column: str = "text"
    dataset_label_column: str = "label"
    dataset_src_column: str = "src"
    # How many rows to keep in memory after shuffling. 0 = keep the whole split.
    dataset_sample_size: int = 5000

    # Mapping from raw model labels to human-readable names
    label_mapping: dict[str, str] = field(
        default_factory=lambda: {
            "LABEL_0": "neutral",
            "LABEL_1": "positive",
            "LABEL_2": "negative",
        }
    )

    app_title: str = "fsociety // sentiment"


_settings = Settings()


def get_settings() -> Settings:
    return _settings