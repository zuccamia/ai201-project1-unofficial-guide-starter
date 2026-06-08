"""Milestone 3: ingestion & chunking for The Unofficial Guide.

`ingest_article(url)` fetches a URL with trafilatura and writes
`documents/<name>.txt` with the citation header from ingestion.md.

`chunk_text(docs)` walks documents/, dispatches to a recursive article
splitter or a Reddit exchange-level packer based on `source_type`, prepends a
provenance breadcrumb, prints 5 representative chunks + the total count, and
returns the chunk list.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Iterable

import tiktoken
import trafilatura
from langchain_text_splitters import RecursiveCharacterTextSplitter

ROOT = Path(__file__).parent
DOCUMENTS_DIR = ROOT / "documents"

TARGET_TOKENS = 400
MIN_TOKENS = 100
MAX_TOKENS = 600
OVERLAP_TOKENS = 50

# URL-based sources (rows 1–12 in planning.md). Rows 13–16 are pre-collected
# under documents/ and are not fetched.
SOURCES: list[dict] = [
    {
        "url": "https://international.northeastern.edu/ogs/current-students/understanding-visa-requirements/guidelines-on-maintaining-status/",
        "out_path": "ogs_maintaining_status.txt",
        "title": "Guidelines on Maintaining Status — Northeastern OGS",
        "source_type": "official_university",
    },
    {
        "url": "https://international.northeastern.edu/ogs/employment/off-campus-employment/f-1-curricular-practical-training/",
        "out_path": "ogs_cpt.txt",
        "title": "F-1 Curricular Practical Training (CPT) — Northeastern OGS",
        "source_type": "official_university",
    },
    {
        "url": "https://international.northeastern.edu/ogs/employment/off-campus-employment/f-1-pre-completion-opt/",
        "out_path": "ogs_pre_completion_opt.txt",
        "title": "F-1 Pre-completion OPT — Northeastern OGS",
        "source_type": "official_university",
    },
    {
        "url": "https://studentemployment.northeastern.edu/f-1/",
        "out_path": "ogs_f1_student_employment.txt",
        "title": "F-1 Student Employment — Northeastern Student Employment",
        "source_type": "official_university",
    },
    {
        "url": "https://international.northeastern.edu/ogs/employment/on-campus-employment/f-1-on-campus-employment/",
        "out_path": "ogs_on_campus_employment.txt",
        "title": "F-1 On-campus Employment — Northeastern OGS",
        "source_type": "official_university",
    },
    {
        "url": "https://international.northeastern.edu/ogs/employment/off-campus-employment/applying-for-post-completion-opt-f-1/",
        "out_path": "ogs_post_completion_opt.txt",
        "title": "Applying for F-1 Post-completion OPT — Northeastern OGS",
        "source_type": "official_university",
    },
    {
        "url": "https://international.northeastern.edu/ogs/current-students/traveling/international-travel/",
        "out_path": "ogs_international_travel.txt",
        "title": "International Travel — Northeastern OGS",
        "source_type": "official_university",
    },
    {
        "url": "https://international.northeastern.edu/ogs/current-students/understanding-visa-requirements/program-extention/",
        "out_path": "ogs_program_extension.txt",
        "title": "Program Extensions — Northeastern OGS",
        "source_type": "official_university",
    },
    {
        "url": "https://international.northeastern.edu/ogs/current-students/understanding-visa-requirements/final-term/",
        "out_path": "ogs_final_term.txt",
        "title": "Final Term — Northeastern OGS",
        "source_type": "official_university",
    },
    {
        "url": "https://international.northeastern.edu/ogs/current-students/understanding-visa-requirements/reduced-course-load/",
        "out_path": "ogs_reduced_course_load.txt",
        "title": "Reduced Course Load — Northeastern OGS",
        "source_type": "official_university",
    },
    {
        "url": "https://graduate.northeastern.edu/knowledge-hub/coop-vs-internship/",
        "out_path": "ogs_coop_vs_internship.txt",
        "title": "Co-op vs. Internship: What's the difference? — Northeastern",
        "source_type": "official_university",
    },
]

_ENCODER = tiktoken.get_encoding("cl100k_base")

_SOURCE_TIER = {
    "official_university": "authoritative",
    "third_party": "advisory",
    "reddit": "advisory",
}


def _tok_len(s: str) -> int:
    return len(_ENCODER.encode(s))


def ingest_article(
    url: str,
    out_path: str | None = None,
    title: str | None = None,
    source_type: str | None = None,
) -> Path:
    """Fetch a URL, extract markdown with trafilatura, prepend the citation
    header, write to documents/<out_path>. Missing args are looked up in SOURCES.
    """
    if out_path is None or title is None or source_type is None:
        for src in SOURCES:
            if src["url"] == url:
                out_path = out_path or src["out_path"]
                title = title or src["title"]
                source_type = source_type or src["source_type"]
                break
        else:
            raise ValueError(
                f"URL not in SOURCES; pass out_path/title/source_type explicitly: {url}"
            )

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
    full_out = DOCUMENTS_DIR / out_path
    full_out.parent.mkdir(parents=True, exist_ok=True)
    full_out.write_text(header + body, encoding="utf-8")
    return full_out


def _parse_header_body(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    sep = "\n---\n"
    if sep not in text:
        return {}, text
    header_text, body = text.split(sep, 1)
    meta: dict = {}
    for line in header_text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, body.lstrip("\n")


def _tier_for(meta: dict) -> str:
    return meta.get("source_tier") or _SOURCE_TIER.get(meta.get("source_type", ""), "peer")


def _breadcrumb(meta: dict) -> str:
    return (
        f"[{meta.get('source_type', 'unknown')} · {_tier_for(meta)} · "
        f"{meta.get('retrieved_at', 'unknown')} · {meta.get('title', 'unknown')}]"
    )


def _merge_below_floor(chunks: list[str]) -> list[str]:
    """Absorb sub-floor fragments into a neighbor so no chunk falls below MIN_TOKENS."""
    out: list[str] = []
    for c in chunks:
        if _tok_len(c) < MIN_TOKENS and out:
            out[-1] = out[-1] + "\n\n" + c
        else:
            out.append(c)
    # If the *first* chunk is still under floor and there's a next one, merge forward.
    if len(out) >= 2 and _tok_len(out[0]) < MIN_TOKENS:
        out[1] = out[0] + "\n\n" + out[1]
        out = out[1:]
    return out


def _chunk_article(body: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=TARGET_TOKENS,
        chunk_overlap=OVERLAP_TOKENS,
        separators=["\n---\n", "\n## ", "\n### ", "\n\n", "\n", " ", ""],
    )
    return _merge_below_floor(splitter.split_text(body))


_REDDIT_SECTION_SEP = re.compile(r"\n---\n")
_REDDIT_HEADING = re.compile(r"^(#{1,3}\s+[^\n]+)\n")
_BLANK_LINE = re.compile(r"\n\s*\n")


def _chunk_reddit(body: str) -> list[str]:
    """Pack Reddit exchanges into chunks up to MAX_TOKENS, never splitting an
    exchange. An exchange = a contiguous block ending at a blank line; child
    replies are indented and carried along with the parent.
    """
    chunks: list[str] = []
    for section in _REDDIT_SECTION_SEP.split(body):
        section = section.strip()
        if not section:
            continue
        m = _REDDIT_HEADING.match(section)
        if m:
            heading = m.group(1)
            section_body = section[m.end():]
        else:
            heading = ""
            section_body = section
        exchanges = [e.strip() for e in _BLANK_LINE.split(section_body) if e.strip()]
        if not exchanges:
            continue

        buf: list[str] = []
        buf_toks = 0
        for ex in exchanges:
            ex_toks = _tok_len(ex)
            if buf and buf_toks + ex_toks > MAX_TOKENS:
                chunks.append(_finalize_reddit(heading, buf))
                buf, buf_toks = [], 0
            buf.append(ex)
            buf_toks += ex_toks
            if buf_toks >= TARGET_TOKENS:
                chunks.append(_finalize_reddit(heading, buf))
                buf, buf_toks = [], 0
        if buf:
            chunks.append(_finalize_reddit(heading, buf))

    return _merge_below_floor(chunks)


def _finalize_reddit(heading: str, exchanges: list[str]) -> str:
    body = "\n\n".join(exchanges)
    return f"{heading}\n\n{body}" if heading else body


def chunk_text(docs: Iterable[Path | str] | None = None) -> list[dict]:
    """Chunk one or more documents under documents/. If `docs` is None, chunks
    every *.txt in DOCUMENTS_DIR. Returns a list of {text, metadata} dicts.
    Prints 5 representative chunks and the total chunk count.
    """
    paths = (
        sorted(DOCUMENTS_DIR.glob("*.txt"))
        if docs is None
        else [Path(d) for d in docs]
    )

    all_chunks: list[dict] = []
    per_doc_counts: list[tuple[str, int]] = []
    for path in paths:
        meta, body = _parse_header_body(path)
        if not body.strip():
            continue
        if meta.get("source_type") == "reddit":
            raw = _chunk_reddit(body)
        else:
            raw = _chunk_article(body)
        breadcrumb = _breadcrumb(meta)
        for i, c in enumerate(raw):
            text = f"{breadcrumb}\n\n{c}"
            all_chunks.append({
                "text": text,
                "metadata": {
                    "source_url": meta.get("source_url", ""),
                    "title": meta.get("title", ""),
                    "source_type": meta.get("source_type", ""),
                    "source_tier": _tier_for(meta),
                    "retrieved_at": meta.get("retrieved_at", ""),
                    "doc_path": str(path.relative_to(ROOT)),
                    "chunk_index": i,
                    "token_count": _tok_len(text),
                },
            })
        per_doc_counts.append((path.name, len(raw)))

    print("\nPer-document chunk counts:")
    for name, n in per_doc_counts:
        print(f"  {name:<45} {n}")
    print(f"\nTotal chunks: {len(all_chunks)}")

    if all_chunks:
        n = len(all_chunks)
        idxs = sorted({0, n // 4, n // 2, (3 * n) // 4, n - 1})[:5]
        print("\n=== 5 representative chunks ===")
        for i in idxs:
            c = all_chunks[i]
            md = c["metadata"]
            print(
                f"\n--- chunk #{i}  "
                f"({md['token_count']} tok · {md['source_type']} · "
                f"{md['source_tier']} · {Path(md['doc_path']).name}) ---"
            )
            text = c["text"]
            print(text if len(text) <= 1000 else text[:1000] + "…")

    return all_chunks


if __name__ == "__main__":
    print("=== Fetching URL-based sources ===")
    for src in SOURCES:
        out = DOCUMENTS_DIR / src["out_path"]
        if out.exists():
            print(f"  skip (exists): {out.name}")
            continue
        print(f"  fetching: {src['url']}")
        try:
            ingest_article(src["url"])
            print(f"    -> wrote {out.name}")
        except Exception as e:
            print(f"    FAILED: {e}")

    print("\n=== Chunking documents/ ===")
    chunk_text()
