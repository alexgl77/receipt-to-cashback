"""LLM extractor — turn raw OCR text into a strict structured receipt.

Step [3] of the spine:
    image -> OCR -> [LLM_EXTRACTOR] -> FAISS match -> CashbackEngine

Design choices (post Yossi feedback):

* **Strict schema via Gemini structured output**, not post-hoc parsing.
  The model is told to return JSON conforming to a Pydantic schema, so
  malformed output is rejected at the SDK boundary, not deep in the
  pipeline.
* **Few-shot prompt** with two CORD-style examples so the model knows
  how messy OCR lines map to clean items.
* **One retry** on validation failure, with the validator's error
  message fed back in. After that we surface a typed exception — the
  Streamlit handler is responsible for showing a graceful error.
* Default model: `gemini-2.5-flash` (the older `gemini-2.0-flash` is
  no longer available to keys created in 2026).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

from google import genai
from google.genai import types
from pydantic import BaseModel, Field, ValidationError


class LineItem(BaseModel):
    name: str = Field(description="Item name exactly as printed on the receipt")
    quantity: int = Field(default=1, ge=1)
    unit_price: float | None = Field(default=None, description="Per-unit price, if printed")
    line_total: float | None = Field(default=None, description="Total for the line (quantity * unit_price)")


class ReceiptExtraction(BaseModel):
    items: list[LineItem] = Field(default_factory=list)
    total: float | None = None
    currency: str | None = Field(default=None, description="ISO 4217 code if inferable, else null")
    merchant: str | None = None
    date: str | None = Field(default=None, description="ISO 8601 if printed, else null")


class LLMExtractionError(RuntimeError):
    """Raised when the LLM fails to produce a schema-valid extraction after retry."""


FEW_SHOT_PROMPT = """\
You receive the raw, noisy OCR output of a single restaurant or café receipt.
Return JSON conforming exactly to the provided schema.

Rules:
- Each printed product/dish/drink line is one item. Use the name exactly as the OCR shows it (do not translate, do not normalise).
- `quantity` is the number printed before the item, default 1 if absent.
- Prices may be printed with commas (e.g. "75,000"), dots, or both — return them as floats. Keep the printed magnitude (do not convert currencies).
- `total` is the grand total of the receipt if it appears; null otherwise.
- `currency` is best-effort. If the receipt clearly uses USD/IDR/KRW etc, return its ISO code; otherwise null.
- Skip lines that are headers, subtotals, tax, change, addresses, phone numbers, "Thank you" messages, plastic-bag fees, or operator codes.

Two examples follow.

Example 1 — OCR:
\"\"\"
Nasi Campur Bali
75,000
Ice Lemon Tea
24,000
SUBTOTAL
99,000
TAX 10%
9,900
TOTAL
108,900
\"\"\"
Expected JSON:
{"items":[{"name":"Nasi Campur Bali","quantity":1,"unit_price":75000,"line_total":75000},{"name":"Ice Lemon Tea","quantity":1,"unit_price":24000,"line_total":24000}],"total":108900,"currency":"IDR","merchant":null,"date":null}

Example 2 — OCR:
\"\"\"
2 x Glazed Donut
5.00
1 x Iced Coffee
3.50
Total
8.50
\"\"\"
Expected JSON:
{"items":[{"name":"Glazed Donut","quantity":2,"unit_price":2.50,"line_total":5.00},{"name":"Iced Coffee","quantity":1,"unit_price":3.50,"line_total":3.50}],"total":8.50,"currency":"USD","merchant":null,"date":null}

Now extract the following OCR. Return ONLY the JSON object, nothing else.

OCR:
\"\"\"
{ocr_text}
\"\"\"
"""


@dataclass
class ExtractorConfig:
    model: str = "gemini-2.5-flash"
    temperature: float = 0.0
    max_retries: int = 1


class LLMExtractor:
    """Extract a `ReceiptExtraction` from raw OCR text using Gemini.

    Usage:
        ext = LLMExtractor()
        result = ext.extract("Nasi Campur Bali\\n75,000\\n...")
        for item in result.items:
            print(item.name, item.line_total)
    """

    def __init__(
        self,
        api_key: str | None = None,
        config: ExtractorConfig | None = None,
    ) -> None:
        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to .env or pass api_key= explicitly."
            )
        self._client = genai.Client(api_key=key)
        self._config = config or ExtractorConfig()

    def extract(self, ocr_text: str) -> ReceiptExtraction:
        # `.replace`, not `.format`: the prompt contains literal `{}` from the
        # JSON example outputs and `str.format` would parse those as fields.
        prompt = FEW_SHOT_PROMPT.replace("{ocr_text}", ocr_text.strip())
        last_error: str | None = None

        for attempt in range(self._config.max_retries + 1):
            user_prompt = prompt
            if last_error is not None:
                user_prompt = (
                    f"{prompt}\n\n"
                    f"Your previous attempt failed schema validation with:\n"
                    f"{last_error}\nReturn corrected JSON only."
                )

            response = self._client.models.generate_content(
                model=self._config.model,
                contents=user_prompt,
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
                        f"Gemini returned non-conforming output after "
                        f"{self._config.max_retries + 1} attempts. "
                        f"Last error: {last_error}\nRaw output preview: {raw[:300]}"
                    ) from exc

        raise LLMExtractionError("unreachable")
