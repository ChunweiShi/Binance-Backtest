from binance.client import Client
from binance.enums import HistoricalKlinesType
import pandas as pd
from datetime import datetime, timedelta

def fetch_klines(symbol, interval, start_str, end_str=None):
    klines = client.get_historical_klines(symbol, interval, start_str, end_str=end_str, klines_type=HistoricalKlinesType.SPOT)
    df = pd.DataFrame(klines, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
    df['Close time'] = pd.to_datetime(df['Close time'], unit='ms')
    return df

# Initialize client
api_key = "your_api_key"
api_secret = "your_api_secret"
client = Client(api_key, api_secret)

# Define time frames
end_time = datetime.utcnow() - timedelta(days=8)
start_time = end_time - timedelta(days=15)

# Fetch data
btcusdt_data = fetch_klines('BTCUSDT', Client.KLINE_INTERVAL_1MINUTE, start_time.strftime("%d %b, %Y"), end_time.strftime("%d %b, %Y"))

# Save to CSV
btcusdt_data.to_csv('btcusdt_1m.csv', index=False)
