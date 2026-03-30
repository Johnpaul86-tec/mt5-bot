def place_trade(symbol, action, lot, sl, tp):
    import MetaTrader5 as mt5

    price = mt5.symbol_info_tick(symbol).ask

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": price - sl * 0.0001,
        "tp": price + tp * 0.0001,
        "deviation": 10,
        "magic": 123456,
        "comment": "AI Bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    return mt5.order_send(request)
