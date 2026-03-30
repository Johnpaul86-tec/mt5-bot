import MetaTrader5 as mt5


def connect_mt5(login, password, server):
    if not mt5.initialize(login=login, password=password, server=server):
        return False
    return True


def get_data(symbol):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 100)
    return rates


def get_trend(rates):
    if rates[-1]["close"] > rates[0]["close"]:
        return "UP"
    return "DOWN"


def generate_signal(symbol):
    rates = get_data(symbol)

    if rates is None or len(rates) < 20:
        return "HOLD"

    trend = get_trend(rates)

    highs = [r["high"] for r in rates]
    lows = [r["low"] for r in rates]

    recent_high = max(highs[-10:])
    previous_high = max(highs[-20:-10])

    recent_low = min(lows[-10:])
    previous_low = min(lows[-20:-10])

    # BUY
    if trend == "UP" and recent_high > previous_high:
        return "BUY"

    # SELL
    if trend == "DOWN" and recent_low < previous_low:
        return "SELL"

    return "HOLD"
