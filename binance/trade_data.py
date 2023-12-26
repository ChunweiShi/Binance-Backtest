from binance.client import Client
from binance.enums import HistoricalKlinesType
import pandas as pd
from datetime import datetime, timedelta

# Initialize client
api_key = ""
api_secret = ""
client = Client(api_key, api_secret)

def fetch_klines(symbol, interval, start_str, end_str=None):
    klines = client.get_historical_klines(symbol, interval, start_str, end_str=end_str, klines_type=HistoricalKlinesType.SPOT)
    df = pd.DataFrame(klines, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
    df['Close time'] = pd.to_datetime(df['Close time'], unit='ms')
    return df

def get_latest_data():

    # Define time frames
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=300)  # Adjusted to get last 300 minutes

    # Fetch 1-minute data
    btcusdt_1m = fetch_klines('BTCFDUSD', Client.KLINE_INTERVAL_1MINUTE, start_time.strftime("%d %b, %Y %H:%M"), end_time.strftime("%d %b, %Y %H:%M"))
    
    return btcusdt_1m

