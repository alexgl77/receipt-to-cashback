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

    `score_threshold` defaults to 0.35 (cosine on MiniLM-L6-v2). Below
    that, items like "PLASTIC BAG SMALL" or operator codes will still
    return *a* match but with low confidence, so the CashbackEngine can
    skip them.
    """
    out: list[MatchedLineItem] = []
    for it in extraction.items:
        m = index.match(it.name)
        out.append(MatchedLineItem(item=it, match=m, accepted=m.score >= score_threshold))
    return out
