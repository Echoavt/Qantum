from __future__ import annotations
from dataclasses import dataclass
from typing import List

@dataclass
class SentimentItem:
    text: str
    score: float

_pipeline = None

def _load_pipeline():
    global _pipeline
    if _pipeline is not None:
        return _pipeline
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline
        model_name = "ProsusAI/finbert"
        tok = AutoTokenizer.from_pretrained(model_name)
        mdl = AutoModelForSequenceClassification.from_pretrained(model_name)
        _pipeline = TextClassificationPipeline(model=mdl, tokenizer=tok, return_all_scores=True)
    except Exception:
        _pipeline = None
    return _pipeline

def score_texts(texts: List[str]) -> List[SentimentItem]:
    pipe = _load_pipeline()
    results: List[SentimentItem] = []
    if pipe is None:
        try:
            from nltk.sentiment import SentimentIntensityAnalyzer
            sia = SentimentIntensityAnalyzer()
            for t in texts:
                s = sia.polarity_scores(t)["compound"]
                results.append(SentimentItem(text=t, score=s))
            return results
        except Exception:
            for t in texts:
                s = 0.0
                tl = t.lower()
                if any(k in tl for k in ["beats","surge","soars","record"]): s = 0.4
                if any(k in tl for k in ["miss","plunge","lawsuit","fraud","cuts"]): s = -0.4
                results.append(SentimentItem(text=t, score=s))
            return results
    for t in texts:
        out = pipe(t)[0]
        by_label = {d["label"].lower(): d["score"] for d in out}
        score = by_label.get("positive", 0) - by_label.get("negative", 0)
        results.append(SentimentItem(text=t, score=score))
    return results
