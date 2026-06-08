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
| 11 | Northeastern University Office of Global Services — Co-op vs. Internship: What's the difference? | official_university | https://graduate.northeastern.edu/knowledge-hub/coop-vs-internship/ |
| 12 | Northeastern University Office of Global Services — Khoury College of Computer Sciences - Silicon Valley - Career Development & Experiential Learning FAQ's | official_university | ./documents/khoury_sv_coop_faq.txt |
| 13 | Reddit — DSO AMA - Part 1 | reddit | ./documents/reddit_dso_ama_part1.txt |
| 14 | Reddit — DSO AMA - Part 2 | reddit | ./documents/reddit_dso_ama_part2.txt |
| 15 | Reddit — STEM-OPT Awareness | reddit | ./documents/reddit_stem_opt_i983_awareness.txt |

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

**Final chunk count:** 156 chunks across 15 documents (Northeastern OGS articles, the Khoury Silicon Valley co-op FAQ, and three Reddit threads). Per-document counts: 3 (`ogs_program_extension`, `ogs_reduced_course_load`) – 25 (`reddit_dso_ama_part1`).

**Representative chunks:**

```
--- chunk #0  (421 tok · official_university · authoritative · khoury_sv_coop_faq.txt) ---
[official_university · authoritative · 2026-06-06 · Co-op Information — Khoury College (Silicon Valley Campus)]

# Co-op Information — Khoury College (Silicon Valley Campus)

## Co-op Durations

Students from Khoury College of Computer Sciences may go on 4-, 6-, or 8-month co-ops, provided they meet all eligibility requirements below. The number of working days permitted depends on the co-op length.

Minimum working days:
- 4 months: 55 business days, falling within either the Fall, Spring, or Summer term
- 6 months: 55 business days during Fall/Spring and 25 business days in Summer 1/2
- 8 months: 55 business days during Fall/Spring and full Summer

Term combinations:
- 4 months: Fall semester only, Spring semester only, or full Summer only
- 6 months: Spring semester & Summer A term, or Summer B term & Fall semester
- 8 months: Spring semester and full Summer, or full Summer and Fall semester

Students are not permitted to go out on back-to-back co-ops between the Fall and Spring sem…
```

```
--- chunk #39  (381 tok · official_university · authoritative · ogs_international_travel.txt) ---
[official_university · authoritative · 2026-06-07 · International Travel — Northeastern OGS]

**Office of Global Services – Available Monday – Friday, 8:30am – 4:30pm EST**

Most importantly, ensure that you cooperate with the officer as much as possible so as not to create further difficulties. More information on Secondary Inspection can be found here.

When entering the U.S., Customs and Border Protection (CBP) officers have the authority to inspect travelers' electronic devices such as phones, tablets, and laptops. These inspections may include viewing content stored on the device, including social media apps and messages. CBP may conduct searches without a warrant, and refusal to comply may affect your ability to enter the U.S. For details, see CBP's policy on electronic device searches. You may also review the following resource from AILA: "Electronic Device Searches at U.S. Ports of Entry": What You Need to Know".

If you are missing documentation or your status is unable to be …
```

```
--- chunk #78  (399 tok · official_university · authoritative · ogs_post_completion_opt.txt) ---
[official_university · authoritative · 2026-06-07 · Applying for F-1 Post-completion OPT — Northeastern OGS]

- Payment Options:
- Copy of your Northeastern transcript (optional)

**Guidance for Mailing an Application to USCIS**

We strongly recommend that you make copies of your complete application for your records before mailing your application to USCIS.

Once you have your documents and I-20 for Post-Completion OPT and you have copied all documentation and assembled the packet, you must send it to the USCIS address below. However its always best practice to confirm the most up-to-date USCIS Direct Filing Addresses for Form I-765 directly on the USCIS website. It is recommended you mail your OPT packet through certified mail which includes a tracking number and guaranteed delivery date.

**Effective 01/08/2021, you will mail your application to the USCIS Chicago lockbox:**

For U.S. Postal Service deliveries:

Attn: I-765 C03

P.O. Box 805373

Chicago, IL 60680-5374


For courier s…
```

```
--- chunk #117  (448 tok · reddit · advisory · reddit_dso_ama_part1.txt) ---
[reddit · advisory · 2026-06-06 · I'm an International Student Advisor/DSO. Ask me your questions!]

## OPT / STEM OPT / green-card interaction

[user] I have an approved I-140, applied for OPT, no job yet, no EAD card. Travel rules?
[DSO] Wait to travel until OPT is approved and you have the EAD card. Get a job to show you're working and in good standing. As long as you haven't filed your I-485, you're good.

[user] Can I apply for the Green Card lottery while on F-1 without affecting OPT eligibility after I graduate next year?
[DSO] It shouldn't affect your OPT. You're encouraged to maintain your underlying status (F-1 → OPT) while the application is pending.

[user] F-1 student doing AOS — will my F-1 status end if I use an AOS EAD card?
[DSO] Yes. I'd recommend keeping your underlying F-1 status until you're approved.

[user] Can I do OPT after F-1 without a job offer? If yes, how?
[DSO | 2] Yes — a job offer isn't required to submit the OPT application. Once approved, you must hav…
```

```
--- chunk #155  (315 tok · reddit · peer · reddit_stem_opt_i983_awareness.txt) ---
[reddit · peer · 2026-06-06 · For Awareness on STEM OPT extension! (state employers dropping Form I-983)]

## Practical takeaways surfaced in the thread (peer advice)

[OP] First confirm STEM OPT eligibility with your university DSO, then ask HR before doing an in-person interview, since interviews cost a lot of effort, money, and time. Also consider calling/emailing HR before even applying.
  [user] You should know eligibility before picking a major — USCIS publishes a list of STEM CIP codes you can check against the code next to your major on your I-20.

[user] The OPT extension timeline is getting worse each year, so network now while you're still on F-1 status — that matters more than the actual job posting. [peer opinion]

## On STEM OPT and "immigrant intent"

[user] How does using STEM OPT after F-1 work? F-1 is a non-immigrant visa with intent to return home after studies.
  [OP] STEM OPT is part of the F-1 framework and is not an immigrant visa. Eligibility is based on complet…
```

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
The system prompt enforces strict grounding: the model can only use facts present in the retrieved `<sources>`, returns a fixed fallback string ("I couldn't find that in the loaded corpus.") when sources don't cover the question, and resists user attempts to override these rules. The prompt then enforces **tier-aware ranking**: each chunk's breadcrumb carries `source_type · tier · retrieved_at · title`, and the model is instructed to anchor on the most authoritative tier present in the sources — `authoritative > advisory > peer` — using retrieval relevance only as a within-tier tiebreaker. When a lower-tier source is clearly more specific to the question, the model may prefer it, but it must attribute advisory or peer-tier claims explicitly ("Per the DSO on Reddit…") and surface contestation when other sources in the context disagree. Time-sensitive claims get "as of {retrieved_at}" framing, and every answer ends with "Not legal advice — confirm specifics with your DSO." A `DISTANCE_THRESHOLD = 1.0` pre-filter drops chunks with Chroma cosine distance > 1.0; if nothing survives the filter, the fallback string is returned without invoking the LLM.

**How source attribution is surfaced in the response:**
Inline citations in the form `[doc_short_name, id]` (e.g. `[ogs_maintaining_status, 1]`), with each id corresponding to a row in the citations panel in the Gradio UI. The panel shows the document, tier, cosine distance, and source URL for every chunk the model saw.

LLM: `llama-3.3-70b-versatile` via Groq.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What documents should I carry when traveling on OPT? | EAD card, offer letter, recent paystubs, I-20 with a valid travel signature, valid passport and visa stamp; if volunteering, a volunteer/employer letter. Should assemble these from multiple thread exchanges rather than returning one. Fail if it surfaces only a single travel exchange and misses items. | Lists passport (6+ mo validity), F-1 visa, I-20 with valid travel signature + OPT recommendation, EAD, paystubs as employment proof; also mentions previous I-20s, financial ability, and current employment evidence. Cites multiple OGS chunks. Does **not** surface the "volunteer/employer letter" detail from the Reddit advisory chunks. | `ogs_pre_completion_opt.txt#13` — authoritative · cosine dist **0.5257** | Partially accurate |
| 2 | What's the official rule on full-time enrollment? | 12 credits for undergraduates, 8 for graduate students (with a reduced figure where an assistantship applies). | Undergraduate: 12 credit hours; Graduate: 8 credit hours (or 9 in 3-credit-enrollment systems); Graduate with assistantship: 6 credit hours. Leads with `ogs_maintaining_status` as the authoritative source. | `ogs_maintaining_status.txt#6` — authoritative · cosine dist **0.4684** | Accurate |
| 3 | Does the $100k H-1B fee apply to a change of status from F-1? | Per the DSO, it does not apply to change-of-status petitions — the fee is described as targeting new petitions for applicants outside the US going through consular processing, and the DSO reported filing COS petitions after Sept 21 with regular fees. | "According to the DSO" — fee does not apply to F-1 → H-1B change of status, only to new H-1B applicants outside the US going through consular processing; notes the DSO filed several COS petitions after the proclamation with regular fees. Citations are clean (no hallucinated ids). **Still misses** the contested-by-attorneys / under-litigation hedge that planning.md's expected answer requires, even though the chunk containing the litigation note (id=4) is in the LLM context — the model pulled the DSO-favorable facts from it but didn't extract the litigation framing. | `reddit_dso_ama_part1.txt#2` — advisory · cosine dist **0.1996** | Partially accurate |
| 4 | What should I do if I need to reduce my course load in the next Fall semester? | A Reduced Course Load is permitted only in three limited situations — academic difficulties, medical conditions, and final academic term of study. For the Fall-semester framing specifically, the relevant paths are the Academic RCL and Medical RCL, and the single most important fact the answer must surface is that prior authorization is required for the Academic and Medical RCL, and students should not drop or withdraw from courses without prior authorization. Students who are in their final academic term of their program of study may qualify for a Final Term RCL if they do not need a full-time course load to complete the requirements for their degree. No prior authorization is needed in this situation. | Describes the three permitted RCL situations at a high level (academic difficulties, medical, final term), then dives into Academic RCL (form Parts 1+2, OGS approval before dropping any course) and Medical RCL (doctor's note → OGS). Adds an attributed Reddit example (Medical RCL for a premature baby). The "failing a class is not a sufficient reason" rule is included. **Misses the Final Term RCL specifics** — the rule that no prior authorization is needed for the final term doesn't surface, because the chunk containing it never made the retrieval top-k. See Failure Case Analysis. | `ogs_final_term.txt#0` — authoritative · cosine dist **0.6141** | Partially accurate |
| 5 | What's the H-1B cap for FY2027? | I couldn't find anything relevant in the loaded corpus. | Returned the fallback verbatim: "I couldn't find that in the loaded corpus." All 7 retrieved chunks were H-1B-fee-adjacent (no FY2027-cap content exists in the corpus). | `reddit_dso_ama_part1.txt#2` — advisory · cosine dist **0.6148** | Accurate |

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

**Question that failed:** "What should I do if I need to reduce my course load in the next Fall semester?" (Q4 in the Evaluation Report.)

**What the system returned:** Description of the **Academic RCL** path (form Parts 1+2 with the academic advisor, submitting the RCL e-form to OGS, waiting for approval before dropping any courses) and the **Medical RCL** path (doctor's note → OGS), plus the rule that a failing grade is not a sufficient reason to apply. The third path — **Final Term RCL** — is missing entirely from the answer, even though planning.md's expected answer lists it as one of the three permitted RCL situations and calls out that it does **not** require prior authorization.

**Root cause (tied to a specific pipeline stage):** **Chunking + retrieval mismatch.** The Final Term RCL rules live in `ogs_final_term.txt` starting at the "Final Term Reduced Courseload (RCL)" section (lines 16-24 of the source file). The chunk that surfaced at RRF #1 for this query was `ogs_final_term.txt#0` — the doc's intro ("Congratulations on approaching the end of your academic program… course load"). The intro semantically matches the query well enough to win the top spot, but it doesn't contain the Final Term RCL rules themselves. The later chunks of `ogs_final_term.txt` that hold the actual RCL specifics never made the top-15 retrieved set, so the LLM never saw them. A contributing factor on the BM25 side: the source page writes "Courseload" as one word, while the query uses "course load" as two — Snowball stemming can't bridge the tokenization gap (`reduce` ↔ `reduced` ✓, `course load` ↔ `courseload` ✗).

**What you would change to fix it:** Two reasonable options.
1. **Re-chunk `ogs_final_term.txt`** so the "Final Term Reduced Courseload (RCL)" section is its own chunk. The current 400-token-target recursive splitter merges the RCL section into a chunk dominated by surrounding administrative text; isolating it would concentrate the RCL-relevant vocabulary and raise both dense and BM25 scores for course-load queries.
2. **Add a small query expansion step** that aliases `course load` → `courseload`, `reduce`/`reduced course load` → `RCL`, before calling `retrieve()`. This is cheaper to implement than re-chunking and would help any future query that hits the same compound-word boundary.

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

- *What I gave the AI:* I flagged that for Q4 ("reduce course load in next Fall semester"), the #1 chunk was coming from `ogs_final_term.txt` instead of `ogs_reduced_course_load.txt`, and asked for the AI's read.
- *What it produced:* A two-part diagnosis — BM25 doesn't stem so `reduce` ≠ `reduced`; MiniLM also sees "next semester" framing as closer to Final Term's intro. Then it implemented Snowball stemming (BM25 rank for the RCL doc jumped 13 → 3), and when that didn't flip #1, offered two next steps: MMR diversity or shrinking the RRF candidate pool.
- *What I changed or overrode:* I chose **pool reduction over MMR** because it was the cheaper experiment to validate. After the AI ran a `POOL_SIZE` sweep (3/5/10/20/50), I **explicitly asked it to re-run all 5 questions** before locking in `POOL_SIZE = 5` — that regression check caught a mild Q2 side-effect (one Reddit chunk surfacing at #5) that the AI hadn't flagged unprompted.

**Instance 2**

- *What I gave the AI:* A complete `SYSTEM_PROMPT` template I wanted to adopt (originally written for a board-game corpus with `[Monopoly, 1]` citations) plus a `DISTANCE_THRESHOLD = 1.0` value, and a directive to update the project docs as it implemented.
- *What it produced:* The prompt adapted to F-1 immigration context (e.g., `[ogs_maintaining_status, 1]` citation format, tier attribution for Reddit / peer claims, a "Not legal advice — confirm with your DSO" closer), the threshold pre-filter wired so all-above-threshold queries return the fallback string **without invoking the LLM**, and updates to `planning.md`, `generation.md`, and `README.md`. Critically, the AI **flagged that the template's "lower id = higher relevance" rule was a divergence from planning.md's original tier-first ranking** and documented that divergence explicitly in the docs rather than silently overwriting the spec.
- *What I changed or overrode:* When I noticed the divergence flagged in the docs, I decided to **revert to the tier-first contract from planning.md**. I had the AI rewrite the prompt's ordering paragraph with tier-anchored language (authoritative > advisory > peer; relevance as a within-tier tiebreaker), revert the divergence notes from the three docs, and re-run the eval. The revert produced one concrete win — Q3's citation hallucination disappeared (`[reddit_dso_ama_part2, 20]` → all ids now valid) — but left two stubborn gaps that need different fixes: Q3's litigation/contested hedge (a generation-extraction problem; the chunk is in context but the model pulled only the DSO-favorable facts from it) and Q4's missing Final Term RCL (an upstream chunking + retrieval miss).
