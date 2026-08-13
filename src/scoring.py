def final_signal(ml_pred, sentiment):
    if ml_pred == 1 and sentiment > 0:
        return "BUY"
    elif ml_pred == 0 and sentiment < 0:
        return "SELL"
    else:
        return "HOLD"
