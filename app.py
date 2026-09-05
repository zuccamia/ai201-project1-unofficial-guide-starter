"""Milestone 5 Gradio interface for The Unofficial Guide.

`python app.py` launches a single-screen Q&A:
  - text input for the question
  - markdown answer with inline [doc, id] citations
  - collapsible panel showing the chunks the model actually saw
"""
from __future__ import annotations

import os
import time
from datetime import datetime

import gradio as gr

from generate import DISTANCE_THRESHOLD, MODEL, generate_from_chunks
from retriever import retrieve

EXAMPLE_QUESTIONS = [
    "What documents should I carry when traveling on OPT?",
    "What's the official rule on full-time enrollment?",
    "Does the $100k H-1B fee apply to a change of status from F-1?",
    "What should I do if I need to reduce my course load in the next Fall semester?",
    "What's the H-1B cap for FY2027?",
]


def _format_citations(citations: list[dict]) -> str:
    if not citations:
        return "_No sources sent to the model — the question fell below the relevance threshold._"
    lines = ["| id | doc | tier | distance | source |", "|---|---|---|---|---|"]
    for c in citations:
        url = c.get("url") or "—"
        url_md = f"[{url}]({url})" if url.startswith("http") else url
        dist = f"{c['distance']:.3f}" if c["distance"] is not None else "—"
        lines.append(f"| {c['id']} | `{c['doc']}` | {c['tier']} | {dist} | {url_md} |")
    return "\n".join(lines)


def _format_chunks(chunks: list[dict]) -> str:
    if not chunks:
        return "_No chunks retrieved._"
    parts = []
    for i, c in enumerate(chunks, 1):
        md = c["metadata"]
        dist = f"{c['distance']:.3f}" if c.get("distance") is not None else "—"
        flag = "" if c.get("distance") is None or c["distance"] <= DISTANCE_THRESHOLD else "  ⚠️ above threshold"
        parts.append(
            f"### #{i} — `{md.get('doc_path', '')}` ({md.get('source_tier', '')}, dist={dist}){flag}\n\n"
            f"```\n{c['text']}\n```"
        )
    return "\n\n---\n\n".join(parts)


def _log_line(msg: str) -> str:
    return f"`{datetime.now().strftime('%H:%M:%S')}` {msg}"


def ask(query: str):
    if not query or not query.strip():
        yield "Enter a question.", "", "", ""
        return

    q = query.strip()
    log: list[str] = [_log_line(f"▶ Received query: _{q}_")]
    yield "", "", "", "\n\n".join(log)

    t0 = time.perf_counter()
    log.append(_log_line("🔍 Retrieving relevant chunks (dense + BM25 with RRF)…"))
    yield "", "", "", "\n\n".join(log)

    raw = retrieve(q)
    kept_count = sum(
        1 for c in raw
        if c.get("distance") is None or c["distance"] <= DISTANCE_THRESHOLD
    )
    dt_r = time.perf_counter() - t0
    log.append(_log_line(
        f"✓ Retrieved {len(raw)} chunks in {dt_r:.2f}s · {kept_count} above the distance threshold"
    ))
    log.append(_log_line(f"✍️ Generating answer with `{MODEL}` via Groq…"))
    yield "", "", "", "\n\n".join(log)

    t1 = time.perf_counter()
    result = generate_from_chunks(q, raw)
    dt_g = time.perf_counter() - t1
    log.append(_log_line(
        f"✓ Answer generated in {dt_g:.2f}s · {len(result['citations'])} citations · total {dt_r + dt_g:.2f}s"
    ))
    yield (
        result["answer"],
        _format_citations(result["citations"]),
        _format_chunks(result["chunks"]),
        "\n\n".join(log),
    )


with gr.Blocks(title="The Unofficial Guide") as demo:
    gr.Markdown(
        "# The Unofficial Guide\n"
        "F-1 visa, OPT/CPT/STEM-OPT, and internships for international students at Northeastern. "
        f"Grounded in a small curated corpus; LLM = `{MODEL}` via Groq.\n\n"
        "> ⏳ **Note:** First load may take ~30 seconds while the server wakes up (free-tier hosting)."
    )
    with gr.Row():
        query = gr.Textbox(
            label="Question",
            placeholder="e.g. What documents should I carry when traveling on OPT?",
            lines=2,
        )
    submit = gr.Button("Ask", variant="primary")
    answer = gr.Markdown(label="Answer")
    with gr.Accordion("Run log", open=True):
        log = gr.Markdown()
    with gr.Accordion("Sources sent to the model", open=False):
        cites = gr.Markdown()
    with gr.Accordion("Raw retrieved chunks (pre-threshold)", open=False):
        raw = gr.Markdown()
    gr.Examples(examples=EXAMPLE_QUESTIONS, inputs=query)
    submit.click(ask, inputs=query, outputs=[answer, cites, raw, log], show_progress="full")
    query.submit(ask, inputs=query, outputs=[answer, cites, raw, log], show_progress="full")


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
