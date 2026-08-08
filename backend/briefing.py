"""
Optional plain-English briefing via Qwen2.5-3B-Instruct.
Direct port of notebook cells 27-28. Heavy (3B params) — lazy-loaded,
only triggered if the client explicitly asks for a briefing, since a
phone-triggered request shouldn't force a multi-GB model load by default.
"""
import torch
from transformers import pipeline

_llm = None


def _get_llm():
    global _llm
    if _llm is None:
        _llm = pipeline(
            "text-generation",
            model="Qwen/Qwen2.5-3B-Instruct",
            torch_dtype=torch.float16,
            device_map="auto",
        )
    return _llm


def generate_briefing(weights, sharpe, tickers, sentiment_scores, ub_array, used_quantum=True):
    table = "\n".join(
        f"- {t}: {w*100:.1f}% allocated | sentiment {s:+.2f} | cap {u*100:.1f}%"
        for t, w, s, u in zip(tickers, weights, sentiment_scores, ub_array)
    )

    prompt = f"""Write a 3-sentence plain-English intro paragraph (no numbers, no lists) for a
portfolio report. Mention that allocation was optimized using Harris Hawks swarm optimization with
a sentiment-based guardrail, and randomness source was {"quantum (Qiskit)" if used_quantum else "classical"}.
Keep it general — do not mention any specific tickers, percentages, or numbers."""

    llm = _get_llm()
    messages = [{"role": "user", "content": prompt}]
    output = llm(messages, max_new_tokens=100, do_sample=False)
    intro = output[0]["generated_text"][-1]["content"]

    return f"""{intro}

Sharpe Ratio: {sharpe:.3f}

{table}
"""
