import pandas as pd
import numpy as np
from collections import defaultdict
def analyze_transactions(transactions):
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])
    # total per category last 30 days
    recent = df[df.date >= (pd.Timestamp.today() - pd.Timedelta(days=30))]
    cat_sum = recent.groupby('category')['amount'].sum().abs().to_dict()
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
    return {"category_spend_last_30d":cat_sum,"subscriptions":subs,"anomalies":anomalies,"tips":tips}

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
