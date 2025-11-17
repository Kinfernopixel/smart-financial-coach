import logging
import json
import random
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..ml.analyzer import analyze_transactions, forecast_goal
from ..services.ai_advisor import AIAdvisor, AIAdvisorError, AIAdvisorUnavailable, top_spending_snapshots

router = APIRouter()

LOGGER = logging.getLogger(__name__)

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "sample_transactions.json"
if not DATA_PATH.exists():
    DATA_PATH = Path(__file__).resolve().parents[4] / "data" / "sample_transactions.json"


class Transaction(BaseModel):
    amount: float
    category: str
    description: str | None = None

class Goal(BaseModel):
    goal_amount: float
    target_date: str


@router.get("/transactions")
def get_transactions():
    if not DATA_PATH.exists():
        return {"transactions": []}
    with DATA_PATH.open() as f:
        return {"transactions": json.load(f)}


@router.post("/transactions")
def add_transaction(tx: Transaction):
    transactions = []
    if DATA_PATH.exists():
        with DATA_PATH.open() as f:
            transactions = json.load(f)

    new_tx = {
        "id": random.randint(1000, 9999),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "merchant": tx.description or "Manual Entry",
        "category": tx.category,
        "amount": tx.amount,
    }
    transactions.append(new_tx)

    try:
        with DATA_PATH.open("w") as f:
            json.dump(transactions, f, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving transaction: {str(e)}")

    return {"message": "Transaction added successfully", "transaction": new_tx}


@router.get("/insights")
def get_insights():
    if not DATA_PATH.exists():
        return {"insights": {}, "trend_insights": []}
    with DATA_PATH.open() as f:
        txs = json.load(f)
    insights = analyze_transactions(txs)
    return {"insights": insights, "trend_insights": insights.get("trend_insights", [])}


@router.get("/forecast")
def forecast(goal_amount: float = 3000.0, months: int = 10):
    if not DATA_PATH.exists():
        return {"forecast": {}}
    with DATA_PATH.open() as f:
        txs = json.load(f)
    return forecast_goal(txs, goal_amount, months)

@router.post("/goal")
def set_goal(goal: Goal):
    """
    Save user's financial goal and return forecast + AI suggestions.
    """
    if not DATA_PATH.exists():
        raise HTTPException(status_code=400, detail="No transactions found")

    with DATA_PATH.open() as f:
        txs = json.load(f)

    # Call the analyzer to forecast progress
    forecast = forecast_goal(txs, goal.goal_amount, months=12)
    insights = analyze_transactions(txs)

    current_balance = sum(t.get("amount", 0.0) for t in txs)
    remaining = goal.goal_amount - current_balance
    months_left = max(1, (datetime.fromisoformat(goal.target_date) - datetime.now()).days // 30)
    monthly_target = remaining / months_left if months_left > 0 else remaining

    fallback = (
        f"You need to save about ${monthly_target:.2f} per month to reach ${goal.goal_amount:.2f} "
        f"by {goal.target_date}. Consider trimming spending in your top category to stay on track."
    )

    advisor = AIAdvisor()
    ai_metadata = {
        "provider": advisor.provider,
        "used": False,
        "error": None,
    }

    recommendation = fallback
    if advisor.is_configured:
        try:
            recommendation = advisor.generate_goal_recommendation(
                goal_amount=goal.goal_amount,
                target_date=goal.target_date,
                forecast=forecast,
                top_spending=top_spending_snapshots(
                    insights.get("category_spend_last_30d", {})
                ),
            )
            ai_metadata["used"] = True
        except (AIAdvisorUnavailable, AIAdvisorError) as exc:
            LOGGER.warning("Falling back to heuristic recommendation: %s", exc)
            ai_metadata["error"] = str(exc)
    else:
        ai_metadata["error"] = "OPENAI_API_KEY not configured"

    return {
        "goal": goal.dict(),
        "forecast": forecast,
        "recommendation": recommendation,
        "ai": ai_metadata,
    }
