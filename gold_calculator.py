def calculate_gold(ounce_price, dollar_price):
    gold_18 = (ounce_price * dollar_price * 0.75) / 31.1034768
    gold_24 = (ounce_price * dollar_price) / 31.1034768

    return {
        "18_carat": round(gold_18),
        "24_carat": round(gold_24)
    }