"""
Historical price data + expected-return/covariance estimates.
Direct port of notebook cell 2 — no API key needed, yfinance is free.
"""
import yfinance as yf


def get_historical_data(tickers, period="180d"):
    data = yf.download(tickers, period=period, progress=False)["Close"]
    data = data.dropna(axis=1, how="all")  # drop tickers with no data (delisted etc.)
    missing = set(tickers) - set(data.columns)
    if missing:
        print(f"⚠️ Skipped (no data): {missing}")
    return data


def get_mu_sigma(tickers, period="180d"):
    price_data = get_historical_data(tickers, period=period)
    returns = price_data.pct_change().dropna()
    mu = returns.mean() * 252
    sigma = returns.cov() * 252
    return mu, sigma
