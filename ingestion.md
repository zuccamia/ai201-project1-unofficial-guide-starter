# Ingestion & Chunking

## Document Ingestion

**Extracting raw text from a URL**
For web sources, a static fetch plus trafilatura handles extraction and cleaning (nav, ads, footer) in one step. The fetcher writes the citation header itself, so provenance is captured at ingestion rather than added later:

```
import trafilatura
from datetime import date

def fetch_to_txt(url: str, out_path: str, title: str, source_type: str = "official_university"):
    html = trafilatura.fetch_url(url)
    if html is None:
        raise RuntimeError(f"fetch failed: {url}")

    body = trafilatura.extract(html, output_format="markdown", include_comments=False)
    if not body:
        raise RuntimeError(f"extraction returned empty — page may be JS-rendered: {url}")

    header = (
        f"source_url: {url}\n"
        f"retrieved_at: {date.today().isoformat()}\n"
        f"title: {title}\n"
        f"source_type: {source_type}\n"
        f"capture_method: trafilatura\n"
        f"---\n\n"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header + body)


if __name__ == "__main__":
    fetch_to_txt(
        "https://international.northeastern.edu/ogs/current-students/understanding-visa-requirements/guidelines-on-maintaining-status/",
        "documents/ogs_maintaining_status.txt",
        title="Guidelines on Maintaining Status — Northeastern OGS",
    )
```

Reddit ended self-serve API access Nov 2025 so Reddit content will be either fetched from the JSON endpoint (appending .json to any Reddit URL to get the public JSON API) or manually captured.


**Expected .txt format**
Each document is one file: a metadata header, a --- separator, then cleaned body text in markdown.

```
source_url: <url, or "internal/access-restricted" for private pages>
retrieved_at: <YYYY-MM-DD>
title: <human-readable title>
source_type: <official_university | reddit | ...>
capture_method: <trafilatura | manual>
---

# <Document title>

## <Section heading>
<cleaned body text…>
```

The header travels with the text so each retrieved chunk can be cited back to its source_url.
Markdown headings (##, ###) are preserved to give the chunker natural semantic split points.
One page = one file = one source_url.

---

## Chunking Strategy

**Chunk size:**
~400 tokens (~1,600 characters), floor ~100, ceiling ~600. Online articles are recursively split down to this on their headings (---/##/###); Reddit threads are packed up to it at the exchange level, keeping each [user]→[DSO] pair whole and concatenating consecutive ones within a topic. The ~400 target matches the natural unit in both — one OGS policy point, or two-to-three related Q&As — while the ceiling stops a chunk from averaging across subtopics and the floor merges away orphan fragments.

**Overlap:**
~50 tokens (~12%), applied only when a long section of an article must be bisected, so a fact landing on the seam (e.g., 60-day vs. 30-day grace period) stays recoverable in both halves.
Reddit threads get zero overlap, because cuts fall between whole exchanges where no fact spans the boundary.
Every chunk also carries a provenance breadcrumb (source_type · source_tier · retrieved_at · title), stored both as prepended text and structured metadata.

**Reasoning:**
The corpus is two structures at once — the online articles behave like a long guide (prose flowing across sentences, so larger chunks + overlap), the threads like a review-heavy set (discrete atomic units, so natural-boundary cuts + no overlap) — which is why a single uniform splitter might undercut both resources.
Accepted tradeoffs: two code paths instead of one, and variable chunk sizes, both worth it for clean retrieval units. We also accept near-duplicate travel/fee Q&As as separate chunks (handled downstream via retrieval diversity rather than by merging, to preserve question–answer integrity), and a few extra tokens per chunk for the breadcrumb — the payoff for tier-aware ranking and citation.

---

## Architecture (stages 1 & 2)

```
+----------------------------------------------------------------------------+
| 1 · DOCUMENT INGESTION                                                     |
|----------------------------------------------------------------------------|
|                                                                            |
|   University articles                   Reddit threads                     |
|   (trafilatura / web_fetch)             (already cleaned + deduped         |
|          |                               by hand: chrome stripped,         |
|          v                               roles tagged, [deleted] dropped)  |
|   Clean OGS articles                             |                         |
|   custom Python: re                              |                         |
|   strip nav / sidebar / footer                   |   (pass through --      |
|          |                                       |    enters chunking      |
|          |                                       |    already clean)       |
|          +------------------+--------------------+                         |
|                             v                                              |
|                  (both streams -> chunking)                                |
|                                                                            |
|   [ dedup deferred: article duplication verified low; Reddit thread dups   |
|     handled at source. ]                                                   |
+----------------------------------------------------------------------------+
                                   |
                                   v
+----------------------------------------------------------------------------+
| 2 · CHUNKING (structure-aware)                                             |
|----------------------------------------------------------------------------|
|                                                                            |
|   University articles               Reddit threads                         |
|   recursive split                   exchange-level packer                  |
|   LangChain                         custom Python;                         |
|   RecursiveCharacterTextSplitter    keep Q->A pairs whole                  |
|   separators: --- ## ### para       token count: tiktoken                  |
|          |                                  |                              |
|          +---------------+------------------+                              |
|                          v                                                 |
|   Prepend provenance breadcrumb                                            |
|   source_type . source_tier . retrieved_at . title                         |
|   target ~400 tok  /  floor 100  /  ceiling 600                            |
+----------------------------------------------------------------------------+
```

---

## Milestone 3 — Ingestion and chunking

I'll give Claude my Document Ingestion and Chunking Strategy markdown file and ask it to implement in an ingest.py file:

- `ingest_article(url)` for items listed in the Documents table with URLs as source
- `chunk_text(docs)` with my specified chunk size and overlap. This should also prints out 5 representative chunks for my inspection, as well as the total counts of chunks.
