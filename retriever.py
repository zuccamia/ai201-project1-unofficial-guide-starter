"""Milestone 4: embedding & hybrid retrieval for The Unofficial Guide.

Persistent ChromaDB collection holds chunks + 384-dim all-MiniLM-L6-v2
embeddings (cosine). `embed_and_store(chunks)` is idempotent — if the
collection already has items, ingestion is treated as done.

`retrieve(query, n_results=15, where=None)` runs hybrid retrieval:
dense (Chroma) and sparse (rank_bm25 over the same chunks), fused with
Reciprocal Rank Fusion (k=60). The `where` filter is applied to both
rankers so they score the same metadata-narrowed subset.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import chromadb
import snowballstemmer
from chromadb.utils import embedding_functions
from rank_bm25 import BM25Okapi

ROOT = Path(__file__).parent
CHROMA_PATH = ROOT / "chroma_db"
COLLECTION_NAME = "unofficial_guide"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
N_RESULTS = 15
RRF_K = 60
POOL_SIZE = 5  # how many to pull from each ranker before fusing — small pool
# preserves tier hygiene by demoting chunks that only one ranker liked
# (a Reddit-paraphrase risk planning.md flagged).


def _embedding_function():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )


def get_collection():
    """Return the persistent Chroma collection, creating it if missing.

    If the collection already exists with items, the caller can skip
    re-ingesting — that's the milestone-4 contract.
    """
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=_embedding_function(),
        metadata={"hnsw:space": "cosine"},
    )


def embed_and_store(chunks: list[dict]) -> Any:
    """Embed each chunk's text with MiniLM and upsert into Chroma.

    Idempotent: if the collection already has items, prints a notice and
    returns without re-embedding.
    """
    collection = get_collection()
    existing = collection.count()
    if existing > 0:
        print(f"[embed_and_store] collection already has {existing} items; skipping.")
        return collection

    ids = [
        f"{c['metadata']['doc_path']}#{c['metadata']['chunk_index']}"
        for c in chunks
    ]
    documents = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    batch = 64
    for i in range(0, len(chunks), batch):
        collection.add(
            ids=ids[i:i + batch],
            documents=documents[i:i + batch],
            metadatas=metadatas[i:i + batch],
        )
    print(f"[embed_and_store] stored {len(chunks)} chunks.")
    return collection


_WORD = re.compile(r"[A-Za-z0-9]+")
_STEMMER = snowballstemmer.stemmer("english")


def _tokenize(text: str) -> list[str]:
    # Snowball-stem so morphology variants collapse for BM25 — e.g. "reduce" and
    # "reduced" both become "reduc". Embeddings already handle this semantically;
    # we only stem the lexical (BM25) side.
    return _STEMMER.stemWords([t.lower() for t in _WORD.findall(text)])


def _matches_where(meta: dict, where: dict) -> bool:
    """Subset of Chroma's where syntax — enough to keep BM25 in lockstep with
    the dense filter for the cases this project uses (eq, $in, $gte/$lte on
    `retrieved_at`, etc.).
    """
    for key, cond in where.items():
        val = meta.get(key)
        if isinstance(cond, dict):
            for op, target in cond.items():
                if op == "$eq" and val != target:
                    return False
                if op == "$ne" and val == target:
                    return False
                if op == "$in" and val not in target:
                    return False
                if op == "$nin" and val in target:
                    return False
                if op == "$gte" and (val is None or val < target):
                    return False
                if op == "$lte" and (val is None or val > target):
                    return False
                if op == "$gt" and (val is None or val <= target):
                    return False
                if op == "$lt" and (val is None or val >= target):
                    return False
        else:
            if val != cond:
                return False
    return True


def retrieve(
    query: str,
    n_results: int = N_RESULTS,
    where: dict | None = None,
) -> list[dict]:
    """Hybrid retrieval with Reciprocal Rank Fusion.

    Returns up to `n_results` dicts: {id, text, metadata, rrf_score,
    dense_rank, bm25_rank}. Either rank may be None if a chunk only
    surfaced in one of the two rankers.
    """
    collection = get_collection()

    dense = collection.query(
        query_texts=[query],
        n_results=POOL_SIZE,
        where=where,
    )
    dense_ids = dense["ids"][0]
    dense_docs = dense["documents"][0]
    dense_metas = dense["metadatas"][0]

    full = collection.get(include=["documents", "metadatas"])
    all_ids = full["ids"]
    all_docs = full["documents"]
    all_metas = full["metadatas"]

    if where:
        keep = [i for i, m in enumerate(all_metas) if _matches_where(m, where)]
        kept_ids = [all_ids[i] for i in keep]
        kept_docs = [all_docs[i] for i in keep]
        kept_metas = [all_metas[i] for i in keep]
    else:
        kept_ids, kept_docs, kept_metas = all_ids, all_docs, all_metas

    if not kept_ids:
        return []

    corpus = [_tokenize(d) for d in kept_docs]
    bm25 = BM25Okapi(corpus)
    scores = bm25.get_scores(_tokenize(query))
    bm25_order = sorted(range(len(scores)), key=lambda i: -scores[i])[:POOL_SIZE]
    bm25_ids = [kept_ids[i] for i in bm25_order]

    rrf: dict[str, float] = {}
    payload: dict[str, dict] = {}
    for rank, doc_id in enumerate(dense_ids):
        rrf[doc_id] = rrf.get(doc_id, 0.0) + 1.0 / (RRF_K + rank + 1)
        payload[doc_id] = {
            "id": doc_id,
            "text": dense_docs[rank],
            "metadata": dense_metas[rank],
            "dense_rank": rank + 1,
            "bm25_rank": None,
        }
    for rank, doc_id in enumerate(bm25_ids):
        rrf[doc_id] = rrf.get(doc_id, 0.0) + 1.0 / (RRF_K + rank + 1)
        if doc_id not in payload:
            i = kept_ids.index(doc_id)
            payload[doc_id] = {
                "id": doc_id,
                "text": kept_docs[i],
                "metadata": kept_metas[i],
                "dense_rank": None,
                "bm25_rank": rank + 1,
            }
        else:
            payload[doc_id]["bm25_rank"] = rank + 1

    fused = sorted(payload.values(), key=lambda x: -rrf[x["id"]])[:n_results]
    for x in fused:
        x["rrf_score"] = rrf[x["id"]]
    return fused


if __name__ == "__main__":
    collection = get_collection()
    if collection.count() == 0:
        from ingest import chunk_text  # lazy: avoid loading at import time
        print("[main] collection empty — chunking and embedding now")
        chunks = chunk_text()
        embed_and_store(chunks)
    else:
        print(f"[main] collection already has {collection.count()} chunks; skipping ingest.")

    eval_queries = [
        "What documents should I carry when traveling on OPT?",
        "What's the official rule on full-time enrollment?",
        "Does the $100k H-1B fee apply to a change of status from F-1?",
        "What should I do if I need to reduce my course load in the next Fall semester?",
        "What's the H-1B cap for FY2027?",
    ]
    for q in eval_queries:
        print(f"\n=== Q: {q} ===")
        hits = retrieve(q, n_results=5)
        if not hits:
            print("  (no hits)")
            continue
        for h in hits:
            md = h["metadata"]
            d = h["dense_rank"] if h["dense_rank"] is not None else "-"
            b = h["bm25_rank"] if h["bm25_rank"] is not None else "-"
            print(
                f"  rrf={h['rrf_score']:.4f}  d={d!s:>3} b={b!s:>3}  "
                f"[{md.get('source_type', ''):<22} {md.get('source_tier', ''):<14}] "
                f"{Path(md.get('doc_path', '')).name}"
            )
