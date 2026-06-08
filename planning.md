# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

```
My unofficial guide focuses on maintaining F-1 visa status and pursuing internships as an international student. This information isn't particularly hard to find, but it consists mostly of rules and regulations that can be confusing to follow and time-consuming to apply to a specific situation or question.
```

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Northeastern University Office of Global Services | Guidelines on maintaining status | https://international.northeastern.edu/ogs/current-students/understanding-visa-requirements/guidelines-on-maintaining-status/ |
| 2 | Northeastern University Office of Global Services | F-1 Curricular Practical Training (CPT) | https://international.northeastern.edu/ogs/employment/off-campus-employment/f-1-curricular-practical-training/ |
| 3 | Northeastern University Office of Global Services | F-1 Pre-completion OPT | https://international.northeastern.edu/ogs/employment/off-campus-employment/f-1-pre-completion-opt/ |
| 4 | Northeastern University Office of Global Services | F-1 Student Employment | https://studentemployment.northeastern.edu/f-1/ |
| 5 | Northeastern University Office of Global Services | On-campus Employment | https://international.northeastern.edu/ogs/employment/on-campus-employment/f-1-on-campus-employment/ |
| 6 | Northeastern University Office of Global Services | Applying for F-1 Post-completion OPT | https://international.northeastern.edu/ogs/employment/off-campus-employment/applying-for-post-completion-opt-f-1/ |
| 7 | Northeastern University Office of Global Services | International travel | https://international.northeastern.edu/ogs/current-students/traveling/international-travel/ |
| 8 | Northeastern University Office of Global Services | Program Extensions | https://international.northeastern.edu/ogs/current-students/understanding-visa-requirements/program-extention/ |
| 9 | Northeastern University Office of Global Services | Final Term | https://international.northeastern.edu/ogs/current-students/understanding-visa-requirements/final-term/ |
| 10 | Northeastern University Office of Global Services | Reduced Course Load | https://international.northeastern.edu/ogs/current-students/understanding-visa-requirements/reduced-course-load/ |
| 11 | Interstride | Your STEM OPT has expired. What now> (2026 update) | https://www.interstride.com/blog/your-stem-opt-visa-has-expired-what-now/ |
| 12 | Northeastern University Office of Global Services | Co-op vs. Internship: What's the difference? | https://graduate.northeastern.edu/knowledge-hub/coop-vs-internship/ |
| 13 | Northeastern University Office of Global Services | Khoury College of Computer Sciences - Silicon Valley - Career Development & Experiential Learning FAQ's | ./documents/khoury_sv_coop_faq.txt |
| 14 | Reddit | DSO AMA - Part 1 | ./documents/reddit_dso_ama_part1.txt |
| 15 | Reddit | DSO AMA - Part 2 | ./documents/reddit_dso_ama_part2.txt |
| 16 | Reddit | STEM-OPT Awareness | ./documents/reddit_stem_opt_i983_awareness.txt |

---

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


## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

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

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
`all-MiniLM-L6-v2`: A lightweight sentence-transformers model that runs locally with no API key or rate limits. It maps text to 384-dimensional vectors, with good performance on short to medium passages. Documents used in this Unofficial Guide mostly include online articles consisting of succinct paragraphs and Reddit threads broken down into short posts and comments. Tradeoffs accepted: lower accuracy than larger models (e.g., OpenAI's `text-embedding-3-large`), but no cost and no latency from network calls.

**Top-k:**
Retrieve k=15 chunks (~6,000 tokens at our ~400-token target, realistically ~4,000–9,000 given variable chunk sizes) and pass them straight to generation, with no rerank or MMR trim for now. Since all 15 go in undifferentiated, the generation prompt enforces tier ranking — authoritative (university office) over advisory (Reddit AMA) — so the model anchors on the most authoritative source rather than the most fluent one. We've accepted that without a diversity step, duplicate-heavy queries (e.g. travel-safety, the $100k fee) may spend a few slots on near-paraphrases; MMR is held in reserve to add only if those answers come back visibly padded.

**Production tradeoff reflection:**
Duplicates in materials like Reddit thread comments are low overhead for manually cleaned and verified documents (which was copy-pasted from web pages as Reddit API is currently restricted). However, production likely means automated scraping to keep the information up-to-date, and retrieval quality may degrade without rigorous cleaning and deduplication before storing. 
Reranking/MMR after retrieval and before feeding context chunks to generation may remediate that, but at the expense of lower latency and computing overhead.

Tier-tagging is another concern for production. Right now, the tier is defined by the source, i.e. university homepage is the authoritative source while Reddit threads are considered advisory, but there are cases where comments on Reddit include statements quoted from official sources or settled regulations that are effectively authoritative.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer | Criteria |
|---|----------|-----------------|----------|
| 1 | What documents should I carry when traveling on OPT? | EAD card, offer letter, recent paystubs, I-20 with a valid travel signature, valid passport and visa stamp; if volunteering, a volunteer/employer letter. Should assemble these from multiple thread exchanges rather than returning one. Fail if it surfaces only a single travel exchange and misses items. | Should assemble these from multiple thread exchanges rather than returning one. Fail if it surfaces only a single travel exchange and misses items. |
| 2 | What's the official rule on full-time enrollment? | 12 credits for undergraduates, 8 for graduate students (with a reduced figure where an assistantship applies). | Should lead with the OGS source and not open with Reddit. Fail if a thread chunk leads. |
| 3 | Does the $100k H-1B fee apply to a change of status from F-1? | Per the DSO, it does not apply to change-of-status petitions — the fee is described as targeting new petitions for applicants outside the US going through consular processing, and the DSO reported filing COS petitions after Sept 21 with regular fees. | The answer must frame this as one advisor's interpretation, note it's contested by other commenters/attorneys, and date it (Oct 2025) / flag it's under litigation — not state it as settled law. Fail if it asserts "no, the fee doesn't apply" flatly without the advisory hedge. |
| 4 | What should I do if I need to reduce my course load in the next Fall semester? | a Reduced Course Load is permitted only in three limited situations — academic difficulties, medical conditions, and final academic term of study. For the Fall-semester framing specifically, the relevant paths are the Academic RCL and Medical RCL, and the single most important fact the answer must surface is that prior authorization is required for the Academic and Medical RCL, and students should not drop or withdraw from courses without prior authorization. Students who are in their final academic term of their program of study may qualify for a Final Term RCL if they do not need a full-time course load to complete the requirements for their degree. No prior authorization is needed in this situation. | The answer should lead with the OGS procedure, includes the prior-authorization rule, and relegates the Reddit version. |
| 5 | What's the H-1B cap for FY2027? | I couldn't find anything relevant in the loaded corpus. | Don't fabricate a number from adjacent fee chunks. Pass = explicit "I don't have that." |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Tier inversion: tier lives in a breadcrumb that we're relying on the generation prompt to honor at k=15 with no reranker. If the prompt under-weights it, or if the authoritative chunk simply doesn't make the top-15 on a query where the advisory phrasing matches better, the model anchors on the fluent-but-wrong source. 

2. Near-duplicate clusters degrading top-k: chunks of texts that are not exact word-by-word duplicates, but are near-paraphrases, can crowd out diverse useful chunks and dilutes the context so the relevant fact gets lost in the middle.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

==============================================================================
 The Unofficial Guide — RAG Pipeline
==============================================================================

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
                                   |
                                   v
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
                                   |
                                   v
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

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

First, I will ask Claude to break down my planning.md into separate markdown files for each of the actionable step in the architecture: DOCUMENT INGESTION, CHUNKING (structure-aware), EMBEDDING + VECTOR STORE, RETRIEVAL, and GENERATION.

**Milestone 3 — Ingestion and chunking:**

I'll give Claude my Document Ingestion and Chunking Strategy markdown file and ask it to implement in an ingest.py file:

- ingest_article(url) for items listed in the Documents table with URLs as source
- chunk_text(docs) with my specified chunk size and overlap. This should also prints out 5 representative chunks for my inspection, as well as the total counts of chunks.

**Milestone 4 — Embedding and retrieval:**

I'll give Claude my Embedding and Retrieval Strategy markdown file and ask it to implement in an retriever.py:

- get_collection() for returning the ChromaDB collection. If collection already exists, ingestion must have been done before and we don't need to ingest again for this project. 
- embed_and_store(chunks) for embedding a list of chunks and store them in ChromeDB
- retrieve(query, n_results=N_RESULTS) for finding the most relevant chunks with metadata prefiltering and hybrid search

**Milestone 5 — Generation and interface:**
