from app.ml.analyzer import analyze_transactions
def test_analyze_empty():
    assert analyze_transactions([]) == {'category_spend_last_30d': {}, 'subscriptions': [], 'anomalies': [], 'tips': []}
