from fastapi import APIRouter
import json, os
from pathlib import Path
from ..ml.analyzer import analyze_transactions, forecast_goal

router = APIRouter()

@router.get("/transactions")
def get_transactions():
    p = Path(__file__).resolve().parents[2] / "data" / "sample_transactions.json"
    # fallback: check top-level data directory
    if not p.exists():
        p = Path(__file__).resolve().parents[4] / "data" / "sample_transactions.json"
    if not p.exists():
        return {"transactions": []}
    with p.open() as f:
        return {"transactions": json.load(f)}

@router.get("/insights")
def get_insights():
    p = Path(__file__).resolve().parents[2] / "data" / "sample_transactions.json"
    if not p.exists():
        p = Path(__file__).resolve().parents[4] / "data" / "sample_transactions.json"
    with p.open() as f:
        txs = json.load(f)
    insights = analyze_transactions(txs)
    return {"insights": insights}

@router.get("/forecast")
def forecast(goal_amount: float = 3000.0, months: int = 10):
    p = Path(__file__).resolve().parents[2] / "data" / "sample_transactions.json"
    if not p.exists():
        p = Path(__file__).resolve().parents[4] / "data" / "sample_transactions.json"
    with p.open() as f:
        txs = json.load(f)
    return forecast_goal(txs, goal_amount, months)
