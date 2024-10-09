import yfinance as yf

def find_best_day_for_SIP(index_name):
  # Step 1: Download the historical data (last 25 years)
  yahoo_data = yf.download(index_name, start='1999-09-30', end='2024-09-30')

  # Step 2: Calculate daily returns
  yahoo_data['Return'] = yahoo_data['Adj Close'].pct_change() + 1  # daily return factor, e.g., 1.01 for 1% return

  yahoo_data['Day of Week'] = yahoo_data.index.dayofweek  # 0 for Monday, 1 for Tuesday, ..., 6 for Sunday

  yahoo_data = yahoo_data.dropna()[3:]

  sip_returns = {0:100, 1:100, 2:100, 3:100, 4:100}
  for index,row in yahoo_data.iterrows():
    for day in sip_returns:
      sip_returns[day] *= row['Return']
    sip_returns[int(row['Day of Week'])] += 100

  # Step 5: Find the best day for SIP by cumulative return
  best_day = max(sip_returns, key=sip_returns.get)

  # Map day number back to weekday names
  days_of_week = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday'}
  best_day_name = days_of_week[best_day]

  # Output the results
  print(f"The best day to invest in {index_name} via SIP over the last 25 years is: {best_day_name}")
  print("Cumulative returns for each day of the week:")
  for day, total_return in sip_returns.items():
      print(f"{days_of_week[day]}: ${total_return:.2f}")


if __name__ == '__main__':
  find_best_day_for_SIP('^GSPC')
  find_best_day_for_SIP('^IXIC')
  find_best_day_for_SIP('^NSEI')