from binance.client import Client
import talib
import numpy as np
import time
from datetime import datetime, timedelta
from trade_data import get_latest_data

# Set up Binance client
api_key = ""
api_secret = ""
client = Client(api_key, api_secret)

# Constants
TRADE_SYMBOL = 'BTCFDUSD'
TRADE_QUANTITY = 0.03
# Function to check BTC balance
def check_btc_balance():
    btc_balance = float(client.get_asset_balance(asset='BTC')['free'])
    return btc_balance >= TRADE_QUANTITY
holding = check_btc_balance()
BBANDS_PERIOD = 111 
STD_DEV_MULTIPLIER = 2.70

# Function to execute a trade
def execute_trade(order_type, symbol, quantity):
    global holding
    try:
        print(f"Sending order {order_type} - Quantity: {quantity}")
        if order_type == 'BUY' and not holding:
            order = client.order_market_buy(symbol=symbol, quantity=quantity)
            holding = True  # Update holding status to True after a buy
        elif order_type == 'SELL' and holding:
            order = client.order_market_sell(symbol=symbol, quantity=quantity)
            holding = False  # Update holding status to False after a sell
        return order
    except Exception as e:
        print(f"An exception occurred - {e}")
        return None

while True:
    latest_data = get_latest_data()
    latest_data['Close'] = latest_data['Close'].astype(float)
    upperband, middleband, lowerband = talib.BBANDS(latest_data['Close'], timeperiod=BBANDS_PERIOD, nbdevup=STD_DEV_MULTIPLIER, nbdevdn=STD_DEV_MULTIPLIER, matype=0)
    latest_data['signal'] = 0
    latest_data.loc[BBANDS_PERIOD:, 'signal'] = np.where(latest_data['Close'][BBANDS_PERIOD:] < lowerband[BBANDS_PERIOD:], 1, np.where(latest_data['Close'][BBANDS_PERIOD:] > upperband[BBANDS_PERIOD:], -1, 0))
    latest_data['position'] = latest_data['signal'].diff()
    if latest_data['position'].iloc[-1] == 1: 
        execute_trade("BUY", TRADE_SYMBOL, TRADE_QUANTITY)
    elif latest_data['position'].iloc[-1] == -1:
        execute_trade("SELL", TRADE_SYMBOL, TRADE_QUANTITY)
    time.sleep(3)
