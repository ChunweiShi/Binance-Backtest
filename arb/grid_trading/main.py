# main.py

import time
from datetime import datetime
from binance.client import Client
from config import API_KEY, API_SECRET, TRADE_SYMBOL, MAX_TRADE_AMOUNT_USD, GRID_SIZE_PERCENT, GRID_BOUND_PERCENT
from config import SLEEP_INTERVAL
from trading_functions import get_realtime_price, calculate_quantity, execute_margin_trade, execute_futures_trade, borrow_asset, repay_asset

def generate_grid_levels(bound_percent, size_percent):
    step = int(100 * size_percent)
    bound = int(100 * bound_percent)
    return [x / 100.0 for x in range(-bound, bound + step, step)]

# main.py

# ... [existing imports and generate_grid_levels function]

client = Client(API_KEY, API_SECRET)
position_quantities = {}  # Track quantities for each grid level
grid_levels = generate_grid_levels(GRID_BOUND_PERCENT, GRID_SIZE_PERCENT)  # Grid levels based on bound percent
last_level = None  # Track the last grid level that was acted upon

def close_positions():
    for level, quantity in position_quantities.items():
        is_long = level < 0
        execute_margin_trade(client, TRADE_SYMBOL, quantity, not is_long)
        execute_futures_trade(client, TRADE_SYMBOL, quantity, is_long)
        if not is_long:
            repay_asset(client, TRADE_SYMBOL, quantity)
    position_quantities.clear()

def adjust_position(level, is_long, price_diff_percent):
    if last_level is not None and abs(last_level) > abs(level):
        close_positions()  # Close all positions if reducing position

    total_trade_amount = MAX_TRADE_AMOUNT_USD * (abs(level) / max(grid_levels))
    existing_trade_amount = sum(position_quantities.values())
    additional_trade_amount = total_trade_amount - existing_trade_amount

    if additional_trade_amount > 0:
        quantity = calculate_quantity(additional_trade_amount, spot_price)
        if is_long:
            execute_margin_trade(client, TRADE_SYMBOL, quantity, True)
            execute_futures_trade(client, TRADE_SYMBOL, quantity, False)
        else:
            borrow_asset(client, TRADE_SYMBOL, quantity)
            execute_margin_trade(client, TRADE_SYMBOL, quantity, False)
            execute_futures_trade(client, TRADE_SYMBOL, quantity, True)
        position_quantities[price_diff_percent] = quantity + position_quantities.get(price_diff_percent, 0)

while True:
    spot_price = get_realtime_price(client, TRADE_SYMBOL, is_future=False)
    futures_price = get_realtime_price(client, TRADE_SYMBOL, is_future=True)
    price_diff_percent = ((futures_price - spot_price) / spot_price) * 100
    price_diff_percent = round(price_diff_percent, 2)

    current_level = None
    for level in grid_levels:
        if abs(price_diff_percent) >= abs(level):
            current_level = level

    if current_level is not None and current_level != last_level:
        is_long = price_diff_percent < 0
        adjust_position(current_level, is_long, price_diff_percent)
        last_level = current_level
        print(f"*** Adjusted {'Long' if is_long else 'Short'} Position at Level {current_level} *** at {datetime.utcnow()} - Diff: {price_diff_percent}%")

    print(f"{datetime.utcnow()}: Monitoring - Spot: {spot_price}, Futures: {futures_price}, Diff: {price_diff_percent}%")
    time.sleep(SLEEP_INTERVAL)