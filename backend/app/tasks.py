from __future__ import annotations
from datetime import datetime, timedelta, timezone
import pandas as pd, numpy as np
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .celery_app import app
from .config import settings
from .storage import SessionLocal, PriceBar, News, Sentiment, Signal
from .services.indicators import build_features
from .services.sentiment import score_texts
from .services.model import predict_prob
from .providers import polygon, newsapi

SPY_TICKERS = ["AAPL","MSFT","NVDA","AMZN","META","GOOGL","BRK.B","AVGO","TSLA"]

@app.task
def ingest_prices():
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=8)
    end = now
    return _ingest_prices_range(SPY_TICKERS, start, end)

@app.task
def ingest_news():
    symbols = SPY_TICKERS
    with SessionLocal() as s:
        for sym in symbols:
            if settings.demo_mode or not settings.newsapi_key:
                rows = [
                    {"title": f"{sym} beats earnings expectations", "description": f"{sym} beats on EPS and revenue."},
                    {"title": f"{sym} faces lawsuit over product safety", "description": f"{sym} involved in class action."},
                ]
            else:
                rows = newsapi.company_news(sym)  # běžně asynchronně, zde zjednodušeno
            if not rows:
                continue
            texts = [f"{r['title']} {r.get('description','')}" for r in rows]
            items = score_texts(texts)
            now = datetime.now(timezone.utc)
            for it in items:
                n = News(symbol=sym, ts=now, title=it.text[:512], summary=None)
                s.add(n)
                s.flush()
                s.add(Sentiment(news_id=n.id, symbol=sym, ts=now, score=it.score))
        s.commit()

@app.task
def update_signals():
    with SessionLocal() as s:
        for sym in SPY_TICKERS:
            q = select(PriceBar).where(PriceBar.symbol==sym).order_by(PriceBar.ts.desc()).limit(600)
            bars = s.execute(q).scalars().all()
            if not bars:
                continue
            df = pd.DataFrame([{k: getattr(b, k) for k in ["ts","open","high","low","close","volume"]} for b in bars]).sort_values("ts")
            q2 = select(Sentiment).where(Sentiment.symbol==sym).order_by(Sentiment.ts.desc()).limit(1)
            last_senti = s.execute(q2).scalars().first()
            senti_val = last_senti.score if last_senti else 0.0
            feat = build_features(df)
            feat["senti"] = senti_val
            prob = float(predict_prob(feat).iloc[-1])
            if prob >= settings.signal_threshold:
                reasons = []
                if senti_val > 0.3:
                    reasons.append("Silně pozitivní sentiment")
                if feat["rsi"].iloc[-1] < 30:
                    reasons.append("Nízké RSI (přeprodané)")
                if feat["macd"].iloc[-1] > feat["macd_signal"].iloc[-1]:
                    reasons.append("MACD býčí křížení")
                s.add(Signal(symbol=sym, ts=df["ts"].iloc[-1], direction="BUY", prob=prob, reasons=" + ".join(reasons) or "Kombinace rysů"))
        s.commit()


def _ingest_prices_range(symbols, start, end):
    with SessionLocal() as s:
        for sym in symbols:
            if settings.demo_mode or not settings.polygon_api_key:
                ts = pd.date_range(start=start, end=end, freq="1min", tz="UTC")
                price = 100 + np.cumsum(np.random.normal(0, 0.05, size=len(ts)))
                high = price + np.random.rand(len(ts))*0.1
                low = price - np.random.rand(len(ts))*0.1
                open_ = price + np.random.normal(0, 0.02, size=len(ts))
                vol = np.random.randint(1000, 5000, size=len(ts))
                rows = [{"ts": t.to_pydatetime(), "open": float(o), "high": float(h), "low": float(l), "close": float(c), "volume": int(v)} for t,o,h,l,c,v in zip(ts, open_, high, low, price, vol)]
            else:
                rows = []  # volání polygon.minute_bars asynchronně v produkci
            for r in rows:
                s.add(PriceBar(symbol=sym, **r))
        try:
            s.commit()
        except IntegrityError:
            s.rollback()
    return {"symbols": symbols}
