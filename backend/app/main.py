from __future__ import annotations
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import asyncio, json, pandas as pd
from .config import settings
from .storage import SessionLocal, init_db, Signal, PriceBar
from .schemas import SignalOut, BacktestRequest, BacktestResult
from .services.backtest import backtest_prob
from .services.model import predict_prob
from .services.indicators import build_features

app = FastAPI(title="MarketAI", version="0.1.0",
              description="Experimentální nástroj; nejde o finanční poradenství.")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

async def get_db():
    async with SessionLocal() as s:
        yield s

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/health")
async def health():
    return {"ok": True, "disclaimer": "This is experimental and not financial advice."}

@app.get("/signals", response_model=list[SignalOut])
async def list_signals(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Signal).order_by(Signal.ts.desc()).limit(100))
    rows = res.scalars().all()
    return [SignalOut(id=r.id, symbol=r.symbol, ts=r.ts, direction=r.direction, prob=r.prob, reasons=r.reasons) for r in rows]

@app.get("/stream/signals")
async def stream_signals(db: AsyncSession = Depends(get_db)):
    async def event_generator():
        last_id = None
        while True:
            res = await db.execute(select(Signal).order_by(Signal.id.desc()).limit(1))
            row = res.scalars().first()
            if row and row.id != last_id:
                last_id = row.id
                data = json.dumps({"id": row.id, "symbol": row.symbol, "ts": row.ts.isoformat(), "direction": row.direction, "prob": row.prob, "reasons": row.reasons})
                yield f"data: {data}\n\n"
            await asyncio.sleep(2)
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/backtest", response_model=BacktestResult)
async def backtest(req: BacktestRequest, db: AsyncSession = Depends(get_db)):
    sym = req.symbols[0]
    res = await db.execute(select(PriceBar).where(PriceBar.symbol==sym).order_by(PriceBar.ts.asc()))
    bars = res.scalars().all()
    if not bars:
        return BacktestResult(trades=0, win_rate=0, sharpe=0, cagr=0, pnl_pct=0)
    df = pd.DataFrame([{k: getattr(b,k) for k in ["ts","open","high","low","close","volume"]} for b in bars])
    df = df[(df["ts"]>=req.start) & (df["ts"]<=req.end)]
    feat = build_features(df); feat["senti"] = 0.0
    prob = predict_prob(feat)
    tmp = pd.DataFrame({"ts": feat["ts"], "close": feat["close"], "prob": prob})
    metrics = backtest_prob(tmp, req.threshold)
    return BacktestResult(**metrics)
