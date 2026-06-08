# Embedding & Retrieval

## Retrieval Approach

**Embedding model:**
`all-MiniLM-L6-v2`: A lightweight sentence-transformers model that runs locally with no API key or rate limits. It maps text to 384-dimensional vectors, with good performance on short to medium passages. Documents used in this Unofficial Guide mostly include online articles consisting of succinct paragraphs and Reddit threads broken down into short posts and comments. Tradeoffs accepted: lower accuracy than larger models (e.g., OpenAI's `text-embedding-3-large`), but no cost and no latency from network calls.

**Top-k:**
Retrieve k=15 chunks (~6,000 tokens at our ~400-token target, realistically ~4,000–9,000 given variable chunk sizes) and pass them straight to generation, with no rerank or MMR trim for now. Since all 15 go in undifferentiated, the generation prompt enforces tier ranking — authoritative (university office) over advisory (Reddit AMA) — so the model anchors on the most authoritative source rather than the most fluent one. We've accepted that without a diversity step, duplicate-heavy queries (e.g. travel-safety, the $100k fee) may spend a few slots on near-paraphrases; MMR is held in reserve to add only if those answers come back visibly padded.

**Production tradeoff reflection:**
Duplicates in materials like Reddit thread comments are low overhead for manually cleaned and verified documents (which was copy-pasted from web pages as Reddit API is currently restricted). However, production likely means automated scraping to keep the information up-to-date, and retrieval quality may degrade without rigorous cleaning and deduplication before storing.
Reranking/MMR after retrieval and before feeding context chunks to generation may remediate that, but at the expense of lower latency and computing overhead.

Tier-tagging is another concern for production. Right now, the tier is defined by the source, i.e. university homepage is the authoritative source while Reddit threads are considered advisory, but there are cases where comments on Reddit include statements quoted from official sources or settled regulations that are effectively authoritative.

---

## Architecture (stages 3 & 4)

```
+----------------------------------------------------------------------------+
| 3 · EMBEDDING + VECTOR STORE                                               |
|----------------------------------------------------------------------------|
|                                                                            |
|   Embed chunks                                                             |
|   sentence-transformers: all-MiniLM-L6-v2  (local, 384-dim)                |
|          |                                                                 |
|          +-------------------+-------------------+                         |
|          v                                       v                         |
|   Store vectors + metadata               Keyword index (for hybrid)        |
|   Chroma (local)                         rank_bm25 / BM25                  |
|   metadata: tier, type, date, title      over the SAME chunks              |
+----------------------------------------------------------------------------+
                                   |
                                   v
+----------------------------------------------------------------------------+
| 4 · RETRIEVAL                                                              |
|----------------------------------------------------------------------------|
|                                                                            |
|   Metadata pre-filter  (tier / source / date; Chroma where=)               |
|                          |                                                 |
|                          v                                                 |
|   Hybrid search:  dense (Chroma, MiniLM)  +  BM25                          |
|                          |                                                 |
|                          v                                                 |
|   Fuse rankings:  Reciprocal Rank Fusion (RRF, k~=60; custom Python)       |
|                          |                                                 |
|                          v                                                 |
|   top-k = 15        [ MMR diversify: HELD in reserve ]                     |
+----------------------------------------------------------------------------+
```

---

## Anticipated Challenges

1. Tier inversion: tier lives in a breadcrumb that we're relying on the generation prompt to honor at k=15 with no reranker. If the prompt under-weights it, or if the authoritative chunk simply doesn't make the top-15 on a query where the advisory phrasing matches better, the model anchors on the fluent-but-wrong source.

2. Near-duplicate clusters degrading top-k: chunks of texts that are not exact word-by-word duplicates, but are near-paraphrases, can crowd out diverse useful chunks and dilutes the context so the relevant fact gets lost in the middle.

---

## Milestone 4 — Embedding and retrieval

I'll give Claude my Embedding and Retrieval Strategy markdown file and ask it to implement in an retriever.py:

- `get_collection()` for returning the ChromaDB collection. If collection already exists, ingestion must have been done before and we don't need to ingest again for this project.
- `embed_and_store(chunks)` for embedding a list of chunks and store them in ChromeDB
- `retrieve(query, n_results=N_RESULTS)` for finding the most relevant chunks with metadata prefiltering and hybrid search
