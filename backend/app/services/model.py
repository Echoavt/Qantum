from __future__ import annotations
import os, joblib
import pandas as pd
from xgboost import XGBClassifier
from ..config import settings

FEATURE_COLS = ["rsi","macd","macd_signal","bb_upper","bb_middle","bb_lower","volatility","vol_change","senti"]
MODEL_PATH = os.path.join(settings.model_dir, "xgb_model.joblib")

def _target_from_future(df: pd.DataFrame, lookahead_hours: int, target_move_pct: float):
    steps = lookahead_hours * 60
    fut = df["close"].shift(-steps)
    ret = (fut - df["close"]) / df["close"] * 100.0
    return (ret > target_move_pct).astype(int)

def train_symbol(df_feat: pd.DataFrame, lookahead_hours: int, target_move_pct: float):
    df = df_feat.dropna().copy()
    if len(df) < 500: return None
    y = _target_from_future(df, lookahead_hours, target_move_pct)
    X = df[FEATURE_COLS]
    mask = y.notna()
    X, y = X[mask], y[mask]
    if y.sum() == 0 or y.sum() == len(y): return None
    model = XGBClassifier(n_estimators=300, max_depth=5, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, eval_metric="logloss", n_jobs=4)
    model.fit(X, y)
    os.makedirs(settings.model_dir, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    return model

def load_model():
    return joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

def predict_prob(df_feat: pd.DataFrame):
    model = load_model()
    if model is None:
        base = 0.5
        rsi = df_feat["rsi"].fillna(50)
        senti = df_feat["senti"].fillna(0)
        prob = base + (senti * 0.25) + ((30 - (rsi.clip(0, 100) - 50).abs())/100)*0.2
        return prob.clip(0.01, 0.99)
    X = df_feat[FEATURE_COLS].fillna(method="ffill").fillna(method="bfill").fillna(0)
    import pandas as pd
    return pd.Series(model.predict_proba(X)[:,1], index=df_feat.index)
