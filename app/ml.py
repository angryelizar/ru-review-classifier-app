import logging
import random
from typing import Any

from datasets import ClassLabel, load_dataset
from huggingface_hub import login
from transformers import pipeline

from app.config import Settings

logger = logging.getLogger(__name__)


class ModelHolder:
    """Holds the inference pipeline and the in-memory dataset sample."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.pipe: Any | None = None
        self.samples: list[dict[str, str]] = []
        self.model_error: str | None = None
        self.dataset_error: str | None = None

    @property
    def model_ready(self) -> bool:
        return self.pipe is not None

    @property
    def dataset_ready(self) -> bool:
        return bool(self.samples)

    def load(self) -> None:
        if self.settings.hf_token:
            login(token=self.settings.hf_token)
            logger.info("Logged in to Hugging Face Hub")
        self._load_model()
        self._load_dataset()

    def _load_model(self) -> None:
        try:
            logger.info("Loading model %s ...", self.settings.model_repo_id)
            self.pipe = pipeline(
                "text-classification",
                model=self.settings.model_repo_id,
                top_k=None,
            )
            logger.info("Model loaded")
        except Exception as exc:  # noqa: BLE001 - keep the app alive for the UI
            self.model_error = f"{type(exc).__name__}: {exc}"
            logger.exception("Failed to load model")

    def _load_dataset(self) -> None:
        try:
            logger.info(
                "Loading dataset %s (split=%s) ...",
                self.settings.dataset_repo_id,
                self.settings.dataset_split,
            )
            ds = load_dataset(
                self.settings.dataset_repo_id,
                self.settings.dataset_config,
                split=self.settings.dataset_split,
            )
            # Shuffle with a random seed on every startup
            ds = ds.shuffle(seed=random.randint(0, 2**32 - 1))
            if self.settings.dataset_sample_size > 0:
                n = min(self.settings.dataset_sample_size, len(ds))
                ds = ds.select(range(n))

            label_feature = ds.features.get(self.settings.dataset_label_column)
            self.samples = [
                {
                    "text": row[self.settings.dataset_text_column],
                    "label": self._label_name(label_feature, row[self.settings.dataset_label_column]),
                    "src": str(row.get(self.settings.dataset_src_column, "")),
                }
                for row in ds
            ]
            logger.info("Dataset loaded: %d samples kept in memory", len(self.samples))
        except Exception as exc:  # noqa: BLE001
            self.dataset_error = f"{type(exc).__name__}: {exc}"
            logger.exception("Failed to load dataset")

    @staticmethod
    def _label_name(feature: Any, value: Any) -> str:
        if isinstance(feature, ClassLabel):
            return feature.int2str(value)
        return str(value)

    def predict(self, text: str) -> dict[str, Any]:
        if not self.model_ready:
            raise RuntimeError(self.model_error or "Model is not loaded")

        result = self.pipe(
            text,
            top_k=None,
            truncation=True,
            max_length=self.settings.model_max_length,
        )
        # Normalize output shape: single text -> flat list of {label, score}
        if result and isinstance(result[0], list):
            result = result[0]

        scores = {
            self.settings.label_mapping.get(item["label"], item["label"]): round(item["score"], 4)
            for item in result
        }
        best = max(result, key=lambda item: item["score"])
        return {
            "label": self.settings.label_mapping.get(best["label"], best["label"]),
            "raw_label": best["label"],
            "score": round(best["score"], 4),
            "scores": scores,
        }

    def random_sample(self) -> dict[str, str]:
        if not self.dataset_ready:
            raise RuntimeError(self.dataset_error or "Dataset is not loaded")
        return random.choice(self.samples)
