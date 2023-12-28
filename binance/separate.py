import pandas as pd
import numpy as np
import talib
import matplotlib.pyplot as plt

# Load your data
df = pd.read_csv('btcfdusd_1m_90d_1227.csv')

def calc_capital(index):
    return usdt + btc * df['Close'][index]

# List to store performance data
performance_data = []

# Iterate over periods and standard deviation multipliers
for period in range(20, 200):
    for std_dev_multiplier in np.arange(1, 5, 0.2):
        usdt = 100000
        btc = 0
        holding = False
        capital_history = []
        commission = 0.00003

        # Calculate Bollinger Bands
        upperband, middleband, lowerband = talib.BBANDS(df['Close'].values, timeperiod=period, nbdevup=std_dev_multiplier, nbdevdn=std_dev_multiplier, matype=0)

        df['signal'] = 0
        df.loc[period:, 'signal'] = np.where(df['Close'][period:] < lowerband[period:], 1, np.where(df['Close'][period:] > upperband[period:], -1, 0))
        df['position'] = df['signal'].diff()

        for i in range(len(df)):
            if df['position'][i] == 1 and not holding:  # Buy
                btc = usdt / df['Close'][i] * (1 - commission)
                usdt = 0
                holding = True
            elif df['position'][i] == -1 and holding:  # Sell
                usdt = btc * df['Close'][i] * (1 - commission)
                btc = 0
                holding = False
            capital_history.append(calc_capital(i))

        total_return = (capital_history[-1] - 100000) / 100000
        performance_data.append((total_return, period, std_dev_multiplier, capital_history))

# Sort by best performance and select top 10
top_10_performances = sorted(performance_data, key=lambda x: x[0], reverse=True)[:10]

# Calculate 'buy and hold' equity curve
initial_btc_for_hold = 100000 / df['Close'][0]
df['hold_value'] = initial_btc_for_hold * df['Close']

# Plotting
plt.figure(figsize=(15, 10))
for i, (return_, period, std_dev, capital_history) in enumerate(top_10_performances):
    plt.subplot(5, 2, i+1)
    plt.plot(capital_history, label=f'Period: {period}, Std Dev: {std_dev:.2f}', color='blue')
    plt.plot(df['hold_value'], label='Buy and Hold', color='orange', alpha=0.5)
    plt.title(f'Top {i+1} Performance: Return {return_:.2%}')
    plt.legend()

plt.tight_layout()
plt.show()

buy_and_hold_return = (df['hold_value'].iloc[-1] - 100000) / 100000
print(f"Buy and Hold Return: {buy_and_hold_return:.2%}")
