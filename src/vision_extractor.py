"""Vision extractor — turn a receipt IMAGE directly into a structured receipt.

Replaces the two-step pipeline (EasyOCR → LLM text parser) with a
single Gemini multimodal call. The motivation, from the day-12
post-mortem on the CORD sample-#1 failures:

* EasyOCR misread "1,591,600" as "591,600" (dropped the leading
  million), and the LLM faithfully parsed the wrong number.
* The OCR→LLM information boundary is a free source of bugs that
  Gemini Vision sidesteps: the model sees the pixels and the digits
  in the same context.

Same `ReceiptExtraction` Pydantic output as `LLMExtractor`, so
`matcher.py`, `vector_store.py`, `cashback_engine.py` and the
drift guard keep working unchanged.

`LLMExtractor` is intentionally kept in the codebase as a fallback /
historical implementation — useful if the API ever blocks vision
calls or for offline tests.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image
from pydantic import ValidationError

from src.llm_extractor import (
    LineItem,                # re-exported for callers that import from here
    LLMExtractionError,      # same exception type — handlers don't change
    ReceiptExtraction,       # same Pydantic schema
)

ImageInput = Image.Image | bytes | str | Path


@dataclass
class VisionExtractorConfig:
    # `gemini-2.5-flash` (not -lite): multimodal, supports image input.
    # -lite was text-only at the time of writing.
    model: str = "gemini-2.5-flash"
    temperature: float = 0.0
    max_retries: int = 1


VISION_PROMPT = """\
You are given a photograph of a printed cash-register receipt. Read it
directly from the image and return JSON conforming exactly to the
provided schema.

Rules:
- Each printed product/dish/drink line is ONE item in `items`. Use the
  name exactly as printed (do not translate, do not normalise).
- If the same item visually appears more than once, output it ONCE
  with the correct quantity. Do not double-count.
- IMPORTANT — PRICE INTERPRETATION: the number printed on the same
  row as a quantity is the LINE TOTAL, not the unit price. For
  "3 x Glazed Donut ... 7.50", set `line_total = 7.50` and
  `unit_price = 7.50 / 3 = 2.50`. Never multiply quantity by the
  printed price.
- Prices may use commas, dots, or both for thousands and decimals
  (e.g. "75,000" in Indonesian Rupiah, "75.00" in USD). Return them
  as floats and keep the printed magnitude (do not convert
  currencies).
- `total` MUST be the grand total of the receipt — the LAST total
  shown, after taxes, service and rounding ("Grand Total", "TOTAL",
  "Total Amount", "Net Total"). Read the digits carefully — a
  leading "1," or similar is easy to miss.
- `currency` is best-effort. ISO 4217 code if inferable
  (IDR, USD, KRW, EUR, ...) otherwise null.
- `merchant` is the trading name printed at the top of the receipt if
  legible. Null otherwise.
- `date` is ISO 8601 (YYYY-MM-DD) if a date is printed. Null otherwise.
- SKIP lines that are subtotals, taxes, service charges, rounding,
  change, cash given, addresses, phone numbers, "Thank you" footers,
  plastic-bag fees and operator codes — none of those are `items`.

Return ONLY the JSON object, nothing else.
"""


class VisionExtractor:
    """Extract a `ReceiptExtraction` from an image using Gemini multimodal."""

    def __init__(
        self,
        api_key: str | None = None,
        config: VisionExtractorConfig | None = None,
    ) -> None:
        # Accept GEMINI_API_KEY (convention) or gemini_api_key (HF Space
        # secret name that someone could realistically set without
        # knowing the Unix uppercase convention).
        key = (
            api_key
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("gemini_api_key")
        )
        if not key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to .env or pass api_key= explicitly."
            )
        self._client = genai.Client(api_key=key)
        self._config = config or VisionExtractorConfig()

    def extract(self, image: ImageInput) -> ReceiptExtraction:
        pil_image = self._to_pil(image)
        last_error: str | None = None

        for attempt in range(self._config.max_retries + 1):
            prompt = VISION_PROMPT
            if last_error is not None:
                prompt = (
                    f"{VISION_PROMPT}\n\nYour previous attempt failed schema "
                    f"validation with:\n{last_error}\n"
                    "Return corrected JSON only."
                )

            response = self._client.models.generate_content(
                model=self._config.model,
                contents=[prompt, pil_image],
                config=types.GenerateContentConfig(
                    temperature=self._config.temperature,
                    response_mime_type="application/json",
                    response_schema=ReceiptExtraction,
                ),
            )

            raw = (response.text or "").strip()
            try:
                payload = json.loads(raw)
                return ReceiptExtraction.model_validate(payload)
            except (json.JSONDecodeError, ValidationError) as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                if attempt == self._config.max_retries:
                    raise LLMExtractionError(
                        f"Gemini Vision returned non-conforming output after "
                        f"{self._config.max_retries + 1} attempts. "
                        f"Last error: {last_error}\n"
                        f"Raw output preview: {raw[:300]}"
                    ) from exc

        raise LLMExtractionError("unreachable")

    @staticmethod
    def _to_pil(image: ImageInput) -> Image.Image:
        if isinstance(image, Image.Image):
            return image.convert("RGB")
        if isinstance(image, bytes):
            return Image.open(BytesIO(image)).convert("RGB")
        if isinstance(image, (str, Path)):
            return Image.open(image).convert("RGB")
        raise TypeError(f"Unsupported image input type: {type(image).__name__}")


# Re-export so callers can do:
#     from src.vision_extractor import VisionExtractor, ReceiptExtraction, LineItem
__all__ = [
    "VisionExtractor",
    "VisionExtractorConfig",
    "ReceiptExtraction",
    "LineItem",
    "LLMExtractionError",
]
