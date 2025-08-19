from datetime import datetime
from pydantic import BaseModel
from typing import List

class SignalOut(BaseModel):
    id: int
    symbol: str
    ts: datetime
    direction: str
    prob: float
    reasons: str

class BacktestRequest(BaseModel):
    symbols: List[str]
    start: datetime
    end: datetime
    threshold: float = 0.75
    lookahead_hours: int = 6
    target_move_pct: float = 1.0

class BacktestResult(BaseModel):
    trades: int
    win_rate: float
    sharpe: float
    cagr: float
    pnl_pct: float
