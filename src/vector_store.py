"""Vector store — FAISS index over the product catalog.

Step [4] of the spine:
    image -> OCR -> LLM JSON -> [FAISS match] -> CashbackEngine

Each catalog row is embedded once at construction time using
sentence-transformers; queries (the `name` of each extracted LineItem)
are embedded on the fly. Cosine similarity is approximated via inner
product on L2-normalised vectors (FAISS' IndexFlatIP).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


@dataclass
class Match:
    sku: str
    name: str
    category: str
    subcategory: str
    typical_price_usd: float
    cashback_rate: float
    score: float  # cosine similarity in [0, 1]


class CatalogIndex:
    """Wrap a FAISS index + the catalog dataframe behind one object.

    Pattern:

        idx = CatalogIndex.from_csv("data/catalog.csv")
        match = idx.match("Iced Lemon Tea")        # best match
        topk  = idx.match_topk("Glazed Donut", 3)  # 3 best matches
    """

    def __init__(
        self,
        catalog: pd.DataFrame,
        model_name: str = DEFAULT_MODEL,
    ) -> None:
        required = {"sku", "name", "category", "subcategory",
                    "typical_price_usd", "cashback_rate"}
        missing = required - set(catalog.columns)
        if missing:
            raise ValueError(f"Catalog missing columns: {missing}")
        self._catalog = catalog.reset_index(drop=True).copy()
        self._model = SentenceTransformer(model_name)
        embeddings = self._embed(self._catalog["name"].tolist())
        self._index = faiss.IndexFlatIP(embeddings.shape[1])
        self._index.add(embeddings)

    @classmethod
    def from_csv(cls, path: str | Path, model_name: str = DEFAULT_MODEL) -> "CatalogIndex":
        return cls(pd.read_csv(path), model_name=model_name)

    def match(self, query: str) -> Match:
        return self.match_topk(query, k=1)[0]

    def match_topk(self, query: str, k: int = 3) -> list[Match]:
        emb = self._embed([query])
        scores, indices = self._index.search(emb, k)
        return [self._row_to_match(i, float(s))
                for s, i in zip(scores[0], indices[0])]

    def _row_to_match(self, row_idx: int, score: float) -> Match:
        row = self._catalog.iloc[row_idx]
        return Match(
            sku=str(row["sku"]),
            name=str(row["name"]),
            category=str(row["category"]),
            subcategory=str(row["subcategory"]),
            typical_price_usd=float(row["typical_price_usd"]),
            cashback_rate=float(row["cashback_rate"]),
            score=score,
        )

    def _embed(self, texts: list[str]) -> np.ndarray:
        vecs = self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return vecs.astype("float32")

    def __len__(self) -> int:
        return len(self._catalog)
