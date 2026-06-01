"""Join a ReceiptExtraction's line items to catalog SKUs via FAISS."""

from __future__ import annotations

from dataclasses import dataclass

from src.llm_extractor import LineItem, ReceiptExtraction
from src.vector_store import CatalogIndex, Match


@dataclass
class MatchedLineItem:
    item: LineItem            # what the LLM extracted
    match: Match              # what FAISS picked from the catalog
    accepted: bool            # True if match.score >= threshold

    @property
    def name(self) -> str:
        return self.item.name

    @property
    def line_total(self) -> float | None:
        return self.item.line_total


def match_extraction(
    extraction: ReceiptExtraction,
    index: CatalogIndex,
    score_threshold: float = 0.35,
) -> list[MatchedLineItem]:
    """Match each extracted LineItem to its nearest catalog SKU.

    `score_threshold` (cosine similarity) gates the `accepted` flag.
    Under the market-research business model the flag does **not**
    decide whether the line earns cashback — every priced line does.
    What it controls is *classification*: accepted lines are tagged
    with the catalog category (food / beverage / …) and contribute to
    the categorised-spend share that data buyers care about;
    rejected lines still pay out at the strategy's base rate but are
    labelled "uncategorized".
    """
    out: list[MatchedLineItem] = []
    for it in extraction.items:
        m = index.match(it.name)
        out.append(MatchedLineItem(item=it, match=m, accepted=m.score >= score_threshold))
    return out
