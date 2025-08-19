import numpy as np
import pandas as pd

def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    roll_up = up.ewm(alpha=1/period, adjust=False).mean()
    roll_down = down.ewm(alpha=1/period, adjust=False).mean()
    rs = roll_up / (roll_down + 1e-12)
    return 100 - (100 / (1 + rs))

def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line, signal_line

def bollinger(close: pd.Series, window: int = 20, k: float = 2.0):
    ma = close.rolling(window).mean()
    std = close.rolling(window).std()
    upper = ma + k * std
    lower = ma - k * std
    return upper, ma, lower

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("ts").copy()
    df["rsi"] = rsi(df["close"])
    macd_line, sig_line = macd(df["close"])
    df["macd"] = macd_line
    df["macd_signal"] = sig_line
    up, mid, low = bollinger(df["close"])
    df["bb_upper"], df["bb_middle"], df["bb_lower"] = up, mid, low
    df["volatility"] = df["close"].pct_change().rolling(30).std() * np.sqrt(252*390)
    df["vol_change"] = df["volume"].pct_change(10)
    return df
