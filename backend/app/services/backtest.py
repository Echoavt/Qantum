import numpy as np
import pandas as pd

def backtest_prob(df: pd.DataFrame, threshold: float, fee_bps: float = 2.0):
    df = df.sort_values("ts").copy()
    df["signal"] = (df["prob"] >= threshold).astype(int)
    df["ret"] = df["close"].pct_change().fillna(0)
    df["strat_ret"] = df["signal"].shift(1).fillna(0) * df["ret"] - (fee_bps/1e4) * (df["signal"].diff().abs().fillna(0))
    cum = (1 + df["strat_ret"]).cumprod()
    pnl_pct = (cum.iloc[-1] - 1.0) * 100
    ann_factor = np.sqrt(252*390)
    sharpe = df["strat_ret"].mean() / (df["strat_ret"].std() + 1e-9) * ann_factor
    wins = ((df["signal"]==1) & (df["ret"]>0)).sum()
    trades = (df["signal"].diff()==1).sum()
    win_rate = wins / max(trades, 1)
    days = (df["ts"].iloc[-1] - df["ts"].iloc[0]).total_seconds() / 86400
    cagr = (cum.iloc[-1]) ** (365.0/max(days,1)) - 1.0
    return {"trades": int(trades), "win_rate": float(win_rate), "sharpe": float(sharpe), "cagr": float(cagr), "pnl_pct": float(pnl_pct)}
