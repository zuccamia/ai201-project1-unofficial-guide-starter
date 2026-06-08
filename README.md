# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

My unofficial guide focuses on maintaining F-1 visa status and pursuing internships as an international student. This information isn't particularly hard to find, but it consists mostly of rules and regulations that can be confusing to follow and time-consuming to apply to a specific situation or question.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Northeastern University Office of Global Services — Guidelines on maintaining status | official_university | https://international.northeastern.edu/ogs/current-students/understanding-visa-requirements/guidelines-on-maintaining-status/ |
| 2 | Northeastern University Office of Global Services — F-1 Curricular Practical Training (CPT) | official_university | https://international.northeastern.edu/ogs/employment/off-campus-employment/f-1-curricular-practical-training/ |
| 3 | Northeastern University Office of Global Services — F-1 Pre-completion OPT | official_university | https://international.northeastern.edu/ogs/employment/off-campus-employment/f-1-pre-completion-opt/ |
| 4 | Northeastern University Office of Global Services — F-1 Student Employment | official_university | https://studentemployment.northeastern.edu/f-1/ |
| 5 | Northeastern University Office of Global Services — On-campus Employment | official_university | https://international.northeastern.edu/ogs/employment/on-campus-employment/f-1-on-campus-employment/ |
| 6 | Northeastern University Office of Global Services — Applying for F-1 Post-completion OPT | official_university | https://international.northeastern.edu/ogs/employment/off-campus-employment/applying-for-post-completion-opt-f-1/ |
| 7 | Northeastern University Office of Global Services — International travel | official_university | https://international.northeastern.edu/ogs/current-students/traveling/international-travel/ |
| 8 | Northeastern University Office of Global Services — Program Extensions | official_university | https://international.northeastern.edu/ogs/current-students/understanding-visa-requirements/program-extention/ |
| 9 | Northeastern University Office of Global Services — Final Term | official_university | https://international.northeastern.edu/ogs/current-students/understanding-visa-requirements/final-term/ |
| 10 | Northeastern University Office of Global Services — Reduced Course Load | official_university | https://international.northeastern.edu/ogs/current-students/understanding-visa-requirements/reduced-course-load/ |
| 11 | Interstride — Your STEM OPT has expired. What now? (2026 update) | | https://www.interstride.com/blog/your-stem-opt-visa-has-expired-what-now/ |
| 12 | Northeastern University Office of Global Services — Co-op vs. Internship: What's the difference? | official_university | https://graduate.northeastern.edu/knowledge-hub/coop-vs-internship/ |
| 13 | Northeastern University Office of Global Services — Khoury College of Computer Sciences - Silicon Valley - Career Development & Experiential Learning FAQ's | official_university | ./documents/khoury_sv_coop_faq.txt |
| 14 | Reddit — DSO AMA - Part 1 | reddit | ./documents/reddit_dso_ama_part1.txt |
| 15 | Reddit — DSO AMA - Part 2 | reddit | ./documents/reddit_dso_ama_part2.txt |
| 16 | Reddit — STEM-OPT Awareness | reddit | ./documents/reddit_stem_opt_i983_awareness.txt |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**
~400 tokens (~1,600 characters), floor ~100, ceiling ~600. Online articles are recursively split down to this on their headings (---/##/###); Reddit threads are packed up to it at the exchange level, keeping each [user]→[DSO] pair whole and concatenating consecutive ones within a topic. The ~400 target matches the natural unit in both — one OGS policy point, or two-to-three related Q&As — while the ceiling stops a chunk from averaging across subtopics and the floor merges away orphan fragments.

**Overlap:**
~50 tokens (~12%), applied only when a long section of an article must be bisected, so a fact landing on the seam (e.g., 60-day vs. 30-day grace period) stays recoverable in both halves.
Reddit threads get zero overlap, because cuts fall between whole exchanges where no fact spans the boundary.
Every chunk also carries a provenance breadcrumb (source_type · source_tier · retrieved_at · title), stored both as prepended text and structured metadata.

**Why these choices fit your documents:**
The corpus is two structures at once — the online articles behave like a long guide (prose flowing across sentences, so larger chunks + overlap), the threads like a review-heavy set (discrete atomic units, so natural-boundary cuts + no overlap) — which is why a single uniform splitter might undercut both resources.
Accepted tradeoffs: two code paths instead of one, and variable chunk sizes, both worth it for clean retrieval units. We also accept near-duplicate travel/fee Q&As as separate chunks (handled downstream via retrieval diversity rather than by merging, to preserve question–answer integrity), and a few extra tokens per chunk for the breadcrumb — the payoff for tier-aware ranking and citation.

**Final chunk count:**

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**
`all-MiniLM-L6-v2`: A lightweight sentence-transformers model that runs locally with no API key or rate limits. It maps text to 384-dimensional vectors, with good performance on short to medium passages. Documents used in this Unofficial Guide mostly include online articles consisting of succinct paragraphs and Reddit threads broken down into short posts and comments. Tradeoffs accepted: lower accuracy than larger models (e.g., OpenAI's `text-embedding-3-large`), but no cost and no latency from network calls.

**Production tradeoff reflection:**
Duplicates in materials like Reddit thread comments are low overhead for manually cleaned and verified documents (which was copy-pasted from web pages as Reddit API is currently restricted). However, production likely means automated scraping to keep the information up-to-date, and retrieval quality may degrade without rigorous cleaning and deduplication before storing.
Reranking/MMR after retrieval and before feeding context chunks to generation may remediate that, but at the expense of lower latency and computing overhead.

Tier-tagging is another concern for production. Right now, the tier is defined by the source, i.e. university homepage is the authoritative source while Reddit threads are considered advisory, but there are cases where comments on Reddit include statements quoted from official sources or settled regulations that are effectively authoritative.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
A tier-aware prompt enforces ranking — authoritative > advisory > peer — so the model anchors on the most authoritative source (university office) over the most fluent one (Reddit AMA). The prompt also includes "as of {date}" framing and a "not legal advice → confirm with your DSO" caveat. Because all k=15 retrieved chunks are passed to generation undifferentiated, the prompt itself is what enforces tier ranking.

**How source attribution is surfaced in the response:**
Citations are pulled from the provenance breadcrumb metadata (source_type · source_tier · retrieved_at · title) attached to each chunk at chunking time.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What documents should I carry when traveling on OPT? | EAD card, offer letter, recent paystubs, I-20 with a valid travel signature, valid passport and visa stamp; if volunteering, a volunteer/employer letter. Should assemble these from multiple thread exchanges rather than returning one. Fail if it surfaces only a single travel exchange and misses items. | | | |
| 2 | What's the official rule on full-time enrollment? | 12 credits for undergraduates, 8 for graduate students (with a reduced figure where an assistantship applies). | | | |
| 3 | Does the $100k H-1B fee apply to a change of status from F-1? | Per the DSO, it does not apply to change-of-status petitions — the fee is described as targeting new petitions for applicants outside the US going through consular processing, and the DSO reported filing COS petitions after Sept 21 with regular fees. | | | |
| 4 | What should I do if I need to reduce my course load in the next Fall semester? | A Reduced Course Load is permitted only in three limited situations — academic difficulties, medical conditions, and final academic term of study. For the Fall-semester framing specifically, the relevant paths are the Academic RCL and Medical RCL, and the single most important fact the answer must surface is that prior authorization is required for the Academic and Medical RCL, and students should not drop or withdraw from courses without prior authorization. Students who are in their final academic term of their program of study may qualify for a Final Term RCL if they do not need a full-time course load to complete the requirements for their degree. No prior authorization is needed in this situation. | | | |
| 5 | What's the H-1B cap for FY2027? | I couldn't find anything relevant in the loaded corpus. | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
