import pandas as pd
import numpy as np
from collections import defaultdict
def analyze_transactions(transactions):
    df = pd.DataFrame(transactions)
    if df.empty:
        return {"category_spend_last_30d": {}, "subscriptions": [], "anomalies": [], "tips": [], "trend_insights": []}

    df['date'] = pd.to_datetime(df['date'])

    today = pd.Timestamp.today().normalize()
    recent_start = today - pd.Timedelta(days=30)
    prior_start = today - pd.Timedelta(days=60)

    # total per category last 30 days
    recent = df[df.date >= recent_start]
    cat_sum = recent.groupby('category')['amount'].sum().abs().to_dict()

    # totals from 30-60 days ago for comparison
    prior = df[(df.date >= prior_start) & (df.date < recent_start)]
    prior_cat_sum = prior.groupby('category')['amount'].sum().abs().to_dict()
    # detect subscriptions: merchant with monthly recurring pattern
    subs = []
    for merchant, group in df.groupby('merchant'):
        months = group.date.dt.to_period('M').nunique()
        if months >= 3 and len(group) >= 3:
            avg = group.amount.mean()
            subs.append({"merchant":merchant,"avg_amount": round(abs(avg),2),"occurrences": len(group)})
    # simple anomaly: category spend > mean+2*std over last 90 days
    last90 = df[df.date >= (pd.Timestamp.today() - pd.Timedelta(days=90))]
    anomalies=[]
    for cat, g in last90.groupby('category'):
        totals = g.groupby(g.date.dt.to_period('M'))['amount'].sum().abs()
        if len(totals)>1:
            z = (totals - totals.mean())/ (totals.std() if totals.std()!=0 else 1)
            if (z>2).any():
                anomalies.append({"category":cat,"months":len(totals),"latest_total": float(totals.iloc[-1])})
    # friendly tips sample
    tips=[]
    if cat_sum.get("Food & Drink",0) > 100:
        tips.append(f"You've spent ${int(cat_sum['Food & Drink'])} on Food & Drink in the last 30 days. Brewing at home could save money.")

    # derive trend insights comparing the last 30 days to the prior 30 days
    advice_lookup = {
        "Food & Drink": "Plan a few low-cost home meals to offset restaurant splurges.",
        "Shopping": "Delay non-essential shopping carts to keep cash flow stable.",
        "Entertainment": "Bundle streaming services or swap for free activities this month.",
        "Transport": "Consider ride-sharing or public transit to soften this uptick.",
        "Travel": "Lock in budgets before booking and watch for fare drops.",
        "Groceries": "Create a list before shopping to avoid impulse buys.",
    }

    trend_rows = []
    categories = set(cat_sum.keys()) | set(prior_cat_sum.keys())
    for category in categories:
        current_total = float(cat_sum.get(category, 0.0))
        previous_total = float(prior_cat_sum.get(category, 0.0))
        if current_total == 0 and previous_total == 0:
            continue
        if previous_total == 0:
            percent_change = 100.0 if current_total > 0 else 0.0
        else:
            percent_change = ((current_total - previous_total) / previous_total) * 100

        if percent_change > 0:
            direction = "increase"
            advice = advice_lookup.get(category, f"Look for easy ways to trim {category} costs next month.")
            sentence = f"Spending on {category} increased {abs(percent_change):.1f}% compared to the prior 30 days."
        elif percent_change < 0:
            direction = "decrease"
            advice = f"Great job lowering {category}! Redirect the savings to your goals."
            sentence = f"Spending on {category} decreased {abs(percent_change):.1f}% from the previous period."
        else:
            direction = "flat"
            advice = f"{category} spending stayed steady—keep monitoring it."
            sentence = f"Spending on {category} stayed roughly the same as the previous month."

        trend_rows.append({
            "category": category,
            "current_total": round(current_total, 2),
            "previous_total": round(previous_total, 2),
            "percent_change": round(percent_change, 1),
            "direction": direction,
            "advice": advice,
            "sentence": sentence,
        })

    trend_rows = sorted(trend_rows, key=lambda x: abs(x["percent_change"]), reverse=True)[:3]

    return {
        "category_spend_last_30d":cat_sum,
        "subscriptions":subs,
        "anomalies":anomalies,
        "tips":tips,
        "trend_insights": trend_rows,
    }

def forecast_goal(transactions, goal_amount=3000.0, months=10):
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])
    # compute average monthly surplus (income - expenses)
    df['month'] = df.date.dt.to_period('M')
    monthly = df.groupby('month')['amount'].sum()  # note income positive or negative depending generator
    # in our generator income is positive; convert to savings: income - expenses
    # treat positives as income, negatives as expense
    monthly_surplus = monthly.apply(lambda x: x if x>0 else x)  # placeholder
    avg_surplus = monthly_surplus.mean() if len(monthly_surplus)>0 else 0
    months_needed = (goal_amount / (avg_surplus if avg_surplus>0 else 1))
    months_needed = min(months, int(np.ceil(months_needed)))
    return {"projected_months_needed": months_needed, "monthly_surplus_estimate": float(avg_surplus)}
