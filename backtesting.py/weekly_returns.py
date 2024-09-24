import yfinance as yf
import pandas as pd
import numpy as np

# Step 1: Download S&P 500 historical data (last 20 years)
sp500 = yf.download('^GSPC', start='2003-09-23', end='2023-09-23')

# Step 2: Calculate daily returns
sp500['Return'] = sp500['Adj Close'].pct_change() + 1  # daily return factor, e.g., 1.01 for 1% return

sp500['Day of Week'] = sp500.index.dayofweek  # 0 for Monday, 1 for Tuesday, ..., 6 for Sunday

sp500 = sp500.dropna()[3:]

sp500

sip_returns = {0:100, 1:100, 2:100, 3:100, 4:100}
for index,row in sp500.iterrows():
  for day in sip_returns:
    sip_returns[day] *= row['Return']
  sip_returns[int(row['Day of Week'])] += 100

# Step 5: Find the best day for SIP by cumulative return
best_day = max(sip_returns, key=sip_returns.get)

# Map day number back to weekday names
days_of_week = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday'}
best_day_name = days_of_week[best_day]

# Output the results
print(f"The best day to invest in S&P 500 SIP over the last 20 years is: {best_day_name}")
print("Cumulative returns for each day of the week:")
for day, total_return in sip_returns.items():
    print(f"{days_of_week[day]}: ${total_return:.2f}")