def convert_price(price_pln, price_dollar, dollar_value: float) -> dict:
    try:
        if price_pln == "":
            price_pln = 0
        if price_dollar == "":
            price_dollar = 0
        price_pln = float(price_pln)
        price_dollar = float(price_dollar)

    except ValueError as e:
        print(e)
        return {"ERROR": "Check input values"}

    if price_pln == 0:
        result_pln: float = round((price_dollar * dollar_value), 2)
        return {"PLN": result_pln}
    if price_dollar == 0:
        result_dollar: float = round((price_pln / dollar_value), 2)
        return {"USD": result_dollar}
