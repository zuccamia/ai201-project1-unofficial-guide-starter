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

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

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

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
