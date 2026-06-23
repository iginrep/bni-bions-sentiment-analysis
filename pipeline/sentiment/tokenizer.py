from __future__ import annotations

"""
model tokenizer wrapper.

Handles text preprocessing → WordPiece tokenization → model-ready tensors.

model: indobenchmark/indobert-base-p1
  - vocab size: 30522 (WordPiece)
  - max seq len: 512
  - tokens: [CLS] text [SEP] [PAD]

Usage:
    from pipeline.sentiment.tokenizer import ModelTokenizer

    tok = ModelTokenizer()
    encoded = tok.encode("aplikasi ini bagus sekali")
    # → {"input_ids": [...], "attention_mask": [...], "token_type_ids": [...]}

    batch = tok.encode_batch(["bagus", "jelek"])
    # → {"input_ids": [[...], [...]], "attention_mask": [[...], [...]], ...}
"""

from typing import Any

from pipeline.sentiment.preprocessing import preprocess

# Default model — indobenchmark/indobert-base-p1 is the standard model
DEFAULT_MODEL = "indobenchmark/indobert-base-p1"
MAX_LENGTH = 512


class ModelTokenizer:
    """Lazy-loading model tokenizer with preprocessing."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        max_length: int = MAX_LENGTH,
        do_lower_case: bool = True,
    ):
        self.model_name = model_name
        self.max_length = max_length
        self.do_lower_case = do_lower_case
        self._tokenizer = None

    @property
    def tokenizer(self):
        if self._tokenizer is None:
            from transformers import AutoTokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                do_lower_case=self.do_lower_case,
            )
        return self._tokenizer

    def preprocess_text(self, text: str) -> str:
        """Apply Indonesian-specific preprocessing before tokenization.

        Uses model mode: clean + normalize, no stopword/stemming removal
        (the model's pre-trained vocabulary handles subword segmentation).
        """
        return preprocess(text, mode="model")

    def encode(
        self,
        text: str,
        max_length: int | None = None,
        padding: str = "max_length",
        truncation: bool = True,
        return_tensors: str | None = None,
    ) -> dict[str, Any]:
        """Encode a single text.

        Returns dict with: input_ids, attention_mask, token_type_ids.
        """
        cleaned = self.preprocess_text(text)
        max_len = max_length or self.max_length
        return self.tokenizer(
            cleaned,
            max_length=max_len,
            padding=padding,
            truncation=truncation,
            return_attention_mask=True,
            return_token_type_ids=True,
            return_tensors=return_tensors,
        )

    def encode_batch(
        self,
        texts: list[str],
        max_length: int | None = None,
        padding: str = "max_length",
        truncation: bool = True,
        return_tensors: str | None = "pt",
    ) -> dict[str, Any]:
        """Encode a batch of texts.

        Returns dict with batched: input_ids, attention_mask, token_type_ids.
        Default return_tensors="pt" → PyTorch tensors.
        """
        cleaned = [self.preprocess_text(t) for t in texts]
        max_len = max_length or self.max_length
        return self.tokenizer(
            cleaned,
            max_length=max_len,
            padding=padding,
            truncation=truncation,
            return_attention_mask=True,
            return_token_type_ids=True,
            return_tensors=return_tensors,
        )

    def decode(self, token_ids: list[int], skip_special_tokens: bool = True) -> str:
        """Decode token IDs back to text."""
        return self.tokenizer.decode(token_ids, skip_special_tokens=skip_special_tokens)

    def tokenize(self, text: str) -> list[str]:
        """Return raw WordPiece tokens (for inspection/debugging)."""
        cleaned = self.preprocess_text(text)
        return self.tokenizer.tokenize(cleaned)

    @property
    def vocab_size(self) -> int:
        return self.tokenizer.vocab_size

    @property
    def pad_token_id(self) -> int:
        return self.tokenizer.pad_token_id

    @property
    def cls_token_id(self) -> int:
        return self.tokenizer.cls_token_id

    @property
    def sep_token_id(self) -> int:
        return self.tokenizer.sep_token_id

    def __repr__(self) -> str:
        loaded = "loaded" if self._tokenizer else "lazy"
        return f"ModelTokenizer(model={self.model_name}, max_len={self.max_length}, {loaded})"
