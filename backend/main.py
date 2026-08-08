import asyncio
from typing import List

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from market_data import get_mu_sigma
from news import fetch_all_ticker_news
from sentiment import score_all_tickers
from harris_hawks import run_hho

app = FastAPI(title="Quantum-Classical Hybrid Portfolio Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_LIMIT = 0.35  # normal max allocation per stock before sentiment adjusts it


class OptimizeRequest(BaseModel):
    tickers: List[str]
    use_quantum: bool = True
    pop_size: int = 25
    max_iter: int = 40
    include_briefing: bool = False  # heavy 3B-param LLM call, off by default


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/portfolio/optimize")
async def optimize_portfolio(req: OptimizeRequest):
    if len(req.tickers) < 2:
        raise HTTPException(400, "Need at least 2 tickers")
    tickers = [t.upper() for t in req.tickers]

    # 1. Historical prices -> mu / Sigma (yfinance, blocking -> thread)
    try:
        mu, sigma = await asyncio.to_thread(get_mu_sigma, tickers)
    except Exception as e:
        raise HTTPException(502, f"Price data fetch failed: {e}")
    if mu.isna().any():
        raise HTTPException(502, "mu contains NaNs — check tickers are valid/liquid")

    # 2. RSS headlines -> FinBERT sentiment
    news_map = await fetch_all_ticker_news(tickers)
    sentiment = await asyncio.to_thread(score_all_tickers, news_map, tickers)

    # 3. Sentiment-driven guardrail
    ub = np.clip(BASE_LIMIT * (1 + sentiment), 0.05, 1.0)

    # 4. Quantum-Levy-guided Harris Hawks optimization
    weights, sharpe = await asyncio.to_thread(
        run_hho, mu.values, sigma.values, ub, len(tickers),
        req.pop_size, req.max_iter, req.use_quantum,
    )

    response = {
        "tickers": tickers,
        "weights": {t: round(float(w), 4) for t, w in zip(tickers, weights)},
        "sharpe": round(float(sharpe), 3),
        "sentiment": {t: round(float(s), 3) for t, s in zip(tickers, sentiment)},
        "cap": {t: round(float(u), 3) for t, u in zip(tickers, ub)},
    }

    if req.include_briefing:
        from briefing import generate_briefing
        response["briefing"] = await asyncio.to_thread(
            generate_briefing, weights, sharpe, tickers, sentiment, ub, req.use_quantum
        )

    return response
