"""
Per-ticker headline fetching over Yahoo Finance RSS feeds.
Direct port of notebook cells 3-4.
"""
import asyncio
import aiohttp
import feedparser


def ticker_rss_url(ticker: str) -> str:
    return f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"


async def fetch_ticker_news(session, ticker, url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with session.get(url, timeout=10, headers=headers) as resp:
            text = await resp.text()
            entries = feedparser.parse(text).entries
            titles = [e.get("title", "") for e in entries[:5]]
            return ticker, titles
    except Exception as e:
        print(f"⚠️ {ticker} failed: {e}")
        return ticker, []


async def fetch_all_ticker_news(tickers: list) -> dict:
    ticker_feeds = {t: ticker_rss_url(t) for t in tickers}
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_ticker_news(session, t, url) for t, url in ticker_feeds.items()]
        results = await asyncio.gather(*tasks)
    return dict(results)


def get_news_map(tickers: list) -> dict:
    """Sync wrapper for use inside FastAPI's async route (called via to_thread)."""
    return asyncio.run(fetch_all_ticker_news(tickers))
