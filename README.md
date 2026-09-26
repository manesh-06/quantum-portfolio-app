# Quantum-Classical Hybrid Portfolio Engine 

Turns the IIIT-Nagpur internship engine (Harris Hawks + Qiskit quantum-random
search + FinBERT sentiment guardrail + Finnhub live data) into a real app on
your phone.

## How it fits together

This is a direct port of your `HHO.ipynb` pipeline into a server + app —
same functions, same logic, no placeholder stand-ins:

- **market_data.py** — `yfinance` price history → expected returns (mu) / covariance (Sigma). No API key needed.
- **news.py** — async RSS pull per ticker from Yahoo Finance feeds (your cells 3-4).
- **sentiment.py** — FinBERT scoring (loads your fine-tuned checkpoint if present, else base `ProsusAI/finbert`).
- **quantum_layer.py** — `quantum_levy_step`: Hadamard-superposes qubits, measures, maps to a ±scale step (cell 16).
- **harris_hawks.py** — `sharpe_fitness` + `run_hho`, exact port of cells 18-19, including the sentiment-driven upper-bound guardrail.
- **briefing.py** — optional Qwen2.5-3B plain-English summary (cells 27-28). Off by default — see caveats below.
- **main.py** — FastAPI endpoint wiring it all together.
- **ios-app/** — SwiftUI app. Thin client. Hits your laptop's IP, shows results.
- **.github/workflows/build-ipa.yml** — builds an **unsigned** `.ipa` on a free
  GitHub-hosted Mac runner. Sideloadly re-signs it at install time with your
  Apple ID, so no certificates or Apple Developer account needed in CI.

## Step 1 — Push this to a GitHub repo

```bash
cd quantum-portfolio-app
git init
git add .
git commit -m "Initial commit"
gh repo create quantum-portfolio-app --public --source=. --push
# or manually: create repo on github.com, then git remote add origin <url> && git push
```

## Step 2 — Trigger the build

Go to your repo → **Actions** tab → "Build iOS IPA" → **Run workflow**.
Takes ~3-5 min. Download the `PortfolioApp-ipa` artifact when it's done —
that's your `.ipa` file.

## Step 3 — Run the backend on your laptop

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

No API key needed — `yfinance` and the Yahoo RSS feeds are both free/keyless.

**Optional: use your fine-tuned FinBERT.** If you ran cell 9 in Colab and
downloaded `finbert-finetuned-final.zip`, unzip it into `backend/finbert-finetuned-final/`
and the server picks it up automatically. Otherwise it falls back to base
`ProsusAI/finbert` so everything still runs.

Find your laptop's local IP (`ipconfig` on Windows, look for IPv4).
Put it in `ios-app/Sources/PortfolioApp/NetworkManager.swift` as `baseURL`,
then re-run the GitHub Action (Step 2) to rebuild with that IP baked in.

## Step 4 — Sideload onto your phone, wired

1. Install **Sideloadly** on Windows: https://sideloadly.io
2. Plug your iPhone into your laptop via USB cable, trust the computer.
3. Open Sideloadly, drag `PortfolioApp.ipa` in.
4. Enter your Apple ID (free one is fine) when prompted — this is what signs
   the app for your device.
5. Hit Start. It installs directly over the wire.
6. On the phone: **Settings → General → VPN & Device Management** → trust
   your Apple ID's developer profile once, then open the app.

Note: a free Apple ID cert expires after 7 days — just re-run Sideloadly to
reinstall. A $99/yr Apple Developer account gives you a 1-year cert instead.

## Step 5 — Use it

Connect phone and laptop to the same WiFi (or USB-tether the phone's
connection through the laptop). Open the app, type tickers, tap Optimize.
It hits your local FastAPI server, which runs the real quantum circuit +
Harris Hawks search + FinBERT sentiment, and returns portfolio weights.

## Notes / honest caveats

- The quantum "randomness" comes from measuring Hadamard-superposed qubits
  on Qiskit Aer (simulator, not real quantum hardware) — matches your
  notebook exactly, and matches what your resume describes.
- FinBERT (~440MB) downloads on first backend request — expect a pause the
  first time you hit "Optimize." The Qwen2.5-3B briefing model is much
  bigger (~6GB) and slow on CPU — leave "Generate AI briefing" off unless
  your laptop has a GPU or you don't mind waiting a couple minutes.
- `run_hho` with `pop_size=25, max_iter=40` and quantum Levy steps calls the
  quantum circuit simulator up to 1,000 times per optimization run — on a
  laptop CPU this can take 10-30+ seconds. The app's request timeout is set
  to 120s to accommodate this; if you hit timeouts, lower `max_iter` in the
  request or in `main.py`'s defaults.
- Yahoo's RSS endpoints occasionally rate-limit or return empty feeds for
  low-volume tickers — `sentiment` will just come back as `0.0` (neutral)
  for those, same as your notebook's fallback behavior.
