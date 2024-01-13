# trading_functions.py

import math
from binance.client import Client
from config import TRADE_SYMBOL
from config import DECIMALS

def get_realtime_price(client, symbol, is_future=False):
    if is_future:
        return round(float(client.futures_symbol_ticker(symbol=symbol)["price"]), 4)
    else:
        return round(float(client.get_symbol_ticker(symbol=symbol)["price"]), 4)

def calculate_quantity(amount_usd, price):
    scaled_quantity = (amount_usd / price) * (10 ** DECIMALS)
    return math.floor(scaled_quantity) / (10 ** DECIMALS)

def execute_margin_trade(client, symbol, quantity, is_buy):
    try:
        side = 'BUY' if is_buy else 'SELL'
        return client.create_margin_order(symbol=symbol, side=side, type='MARKET', quantity=quantity, isIsolated='TRUE')
    except Exception as e:
        print(f"Margin trade error: {e}")

def execute_futures_trade(client, symbol, quantity, is_buy):
    try:
        side = 'BUY' if is_buy else 'SELL'
        return client.futures_create_order(symbol=symbol, side=side, type='MARKET', quantity=quantity)
    except Exception as e:
        print(f"Futures trade error: {e}")

def borrow_asset(client, symbol, amount):
    try:
        asset = symbol[:-4]  # Assuming the asset is the prefix of the symbol (e.g., XAI in XAIUSDT)
        return client.create_margin_loan(asset=asset, isIsolated='TRUE', symbol=symbol, amount=amount)
    except Exception as e:
        print(f"Borrow asset error: {e}")

def repay_asset(client, symbol, amount):
    try:
        asset = symbol[:-4]
        return client.repay_margin_loan(asset=asset, isIsolated='TRUE', symbol=symbol, amount=amount)
    except Exception as e:
        print(f"Repay asset error: {e}")