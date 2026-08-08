"""
Sentiment scoring, matching notebook cells 8 & 14.

If you downloaded finbert-finetuned-final.zip from the Colab (cell 9),
unzip it into backend/finbert-finetuned-final/ and this will load your
fine-tuned model automatically. Otherwise it falls back to base
ProsusAI/finbert so the pipeline still runs end-to-end.
"""
import os
import numpy as np
from transformers import pipeline

_FINETUNED_PATH = os.path.join(os.path.dirname(__file__), "finbert-finetuned-final")
_model = None


def _get_model():
    global _model
    if _model is None:
        if os.path.isdir(_FINETUNED_PATH):
            print(f"Loading fine-tuned FinBERT from {_FINETUNED_PATH}")
            _model = pipeline("sentiment-analysis", model=_FINETUNED_PATH, tokenizer=_FINETUNED_PATH)
        else:
            print("Fine-tuned checkpoint not found, using base ProsusAI/finbert")
            _model = pipeline("sentiment-analysis", model="ProsusAI/finbert")
    return _model


def get_sentiment_score(headlines: list, model=None) -> float:
    model = model or _get_model()
    if not headlines:
        return 0.0  # no news = neutral, no adjustment
    scores = []
    for h in headlines:
        result = model(h)[0]
        label = result["label"]
        conf = result["score"]
        if label == "positive":
            scores.append(conf)
        elif label == "negative":
            scores.append(-conf)
        else:
            scores.append(0.0)
    return float(np.mean(scores))


def score_all_tickers(news_map: dict, tickers: list) -> np.ndarray:
    model = _get_model()
    return np.array([get_sentiment_score(news_map.get(t, []), model) for t in tickers])
