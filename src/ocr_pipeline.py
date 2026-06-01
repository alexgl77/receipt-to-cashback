"""OCR pipeline — turn a receipt image into raw text lines.

Used as step [2] of the receipt-to-cashback spine:
    image -> CNN gate -> [OCR_PIPELINE] -> LLM extractor -> FAISS -> CashbackEngine

Backed by EasyOCR (CRAFT detector + CRNN recognizer). EasyOCR was
chosen over TrOCR for the MVP because it ships detection +
recognition in one call, runs on CPU, and produced 100% recall on the
day-3 smoke test against CORD-v2 ground-truth menus.
"""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Sequence

import easyocr
import numpy as np
from PIL import Image

ImageInput = Image.Image | np.ndarray | bytes | str | Path


@dataclass
class OCRLine:
    text: str
    confidence: float
    bbox: tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]]


class OCRPipeline:
    """Wrap EasyOCR with a stable interface for the rest of the app.

    The point of having a class (rather than a free function) is two-fold:
    the EasyOCR Reader is heavy to construct (downloads + loads weights),
    so we want to instantiate it once per app lifetime; and we want a
    single place to swap the backend if we ever upgrade to TrOCR or Donut.
    """

    def __init__(
        self,
        languages: Sequence[str] = ("en",),
        gpu: bool = False,
    ) -> None:
        self._reader = easyocr.Reader(list(languages), gpu=gpu, verbose=False)

    def read_lines(self, image: ImageInput) -> list[OCRLine]:
        """Return detected text lines, top-to-bottom, with confidence + bbox."""
        arr = self._to_numpy(image)
        raw = self._reader.readtext(arr, detail=1, paragraph=False)
        lines = [
            OCRLine(text=str(text), confidence=float(conf), bbox=tuple(map(tuple, bbox)))
            for bbox, text, conf in raw
        ]
        lines.sort(key=lambda ln: (ln.bbox[0][1], ln.bbox[0][0]))  # y then x
        return lines

    def read_text(self, image: ImageInput, separator: str = "\n") -> str:
        """Return one big string, lines joined top-to-bottom.

        This is the format the LLM extractor will receive in step [3].
        """
        return separator.join(ln.text for ln in self.read_lines(image))

    @staticmethod
    def _to_numpy(image: ImageInput) -> np.ndarray:
        if isinstance(image, np.ndarray):
            return image
        if isinstance(image, Image.Image):
            return np.array(image.convert("RGB"))
        if isinstance(image, (str, Path)):
            return np.array(Image.open(image).convert("RGB"))
        if isinstance(image, bytes):
            return np.array(Image.open(BytesIO(image)).convert("RGB"))
        raise TypeError(f"Unsupported image input type: {type(image).__name__}")
