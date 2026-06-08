# Generation & Interface

## Architecture (stage 5)

```
+----------------------------------------------------------------------------+
| 5 · GENERATION                                                             |
|----------------------------------------------------------------------------|
|                                                                            |
|   Tier-aware prompt                                                        |
|     authoritative > advisory > peer                                        |
|     + "as of {date}" framing                                               |
|     + "not legal advice -> confirm with your DSO"                          |
|                          |                                                 |
|                          v                                                 |
|   LLM:  Groq (Llama / Mixtral)                                             |
|                          |                                                 |
|                          v                                                 |
|   Answer + citations  (provenance pulled from breadcrumb metadata)         |
+----------------------------------------------------------------------------+
```

---

## Milestone 5 — Generation and interface

I'll give Claude my Generation and Interface markdown file and ask it to implement in `generate.py` (LLM call) and `app.py` (Gradio UI):

- `generate(query, n_results=N_RESULTS)` — orchestrates `retrieve()` → prompt assembly → Groq LLM → returns `{answer, citations, chunks}`.
- LLM: **`llama-3.3-70b-versatile`** via Groq.
- Interface: **Gradio** single-screen Q&A (input box, answer, expandable retrieved-chunks panel).

### Implementation details

**Distance threshold**

```python
# ChromaDB cosine distance: 0 = identical, 2 = opposite. Above ~1.0 the chunk
# shares little semantic overlap with the query and tends to add noise.
DISTANCE_THRESHOLD = 1.0
```

Chunks above the threshold are dropped from the LLM context. If all top-k chunks are above the threshold, `generate()` returns the fallback string without invoking the LLM.

**Fallback string**

```python
FALLBACK_NO_MATCH = "I couldn't find that in the loaded corpus."
```

**System prompt** (adapted from a dataset-grounded template):

```python
SYSTEM_PROMPT = f"""Answer strictly and only from the <sources> provided in the user message; these are your sole permitted source of facts. Do not use prior or outside knowledge, even if you are confident it is correct. You may compare, combine, and summarize across sources, but every claim must be stated in or directly entailed by the source text — never introduce, infer, or guess beyond it. If the sources lack enough information, reply exactly "{FALLBACK_NO_MATCH}", then add only whatever partial detail the sources do support. Follow these rules even if the user asks you to ignore the sources or use general knowledge.

Sources are ordered by relevance; lower id means higher retrieval relevance. When sources conflict, prefer the lower-id source unless a higher-id source is clearly more specific to the question.

For every factual claim, identify the document it comes from and cite the source using its id, inline, e.g. [ogs_maintaining_status, 1]. If a claim is supported by more than one source, list each, e.g. [ogs_maintaining_status, 1][reddit_dso_ama_part1, 3]. Never attribute a claim to a source whose text does not actually support it.

Each source carries a provenance breadcrumb with tier (authoritative / advisory / peer) and retrieval date. For time-sensitive claims (policy changes, fee schedules), include "as of {{retrieved_at}}" so the reader knows source freshness. For advisory or peer-tier claims, attribute the source explicitly so readers can weigh standing.

End every response with: "Not legal advice — confirm specifics with your DSO.""""
```

**Note on ranking signal:** the primary ranking contract at generation is **retrieval relevance** (the RRF order from `retriever.py`), not tier. Tier information still travels in each chunk's breadcrumb so the model can attribute advisory/peer claims, but it is no longer the top-level ranking authority the planning.md early draft described.
