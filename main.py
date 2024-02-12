import yfinance as yf
import pandas as pd
import sys
import matplotlib.pyplot as plt
import backtesting
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

# Check if at least one ticker symbol is provided
if len(sys.argv) < 2:
    print("Please provide at least one ticker symbol as an argument, separated by commas if multiple.")
    sys.exit()

# Split the input argument into a list of ticker symbols
tickers = sys.argv[1].split(',')
is_short_below_long_trend = False


def is_within_range(short, long, percent):
    # Calculate the difference between the last elements of short and long
    difference = abs(short[-1] - long[-1])

    # Calculate 10% of the last element of the 'long' list
    ten_percent_of_long = percent * abs(long[-1])

    # Check if the difference is less than or equal to 10% of the last element of 'long'
    if difference <= ten_percent_of_long:
        return True
    return False


def is_increasing(price_data, days):
    price_data_length = len(price_data)
    derivative = (price_data[price_data_length - 1] - price_data[price_data_length - (days + 1)]) / days
    if derivative > 0:
        return True
    return False


# Iterate over each ticker symbol
for ticker in tickers:
    #print(f"Analyzing {ticker}...")
    try:
        # Fetch stock data using yfinance
        stock = yf.Ticker(ticker)
        df = stock.history(period="5y")

        # Check if the dataframe is empty
        if df.empty:
            print(f"No data found for {ticker}, skipping...")
            continue

        # Calculate short-term and long-term moving averages
        df['short_short_ma'] = df['Close'].rolling(window=15).mean()
        df['short_ma'] = df['Close'].rolling(window=50).mean()
        df['long_ma'] = df['Close'].rolling(window=200).mean()

        # Add date column
        df['Date'] = df.index

        # Iterate over rows and check for cross point
        for i in range(len(df)):
            if (df['short_ma'].iloc[i] > df['long_ma'].iloc[i]) and (df['short_ma'].iloc[i - 1] < df['long_ma'].iloc[i - 1]):
                # print(f"Buy on: {df['Date'][i]} for {ticker}")
                is_short_below_long_trend = False
            elif (df['short_ma'].iloc[i] < df['long_ma'].iloc[i]) and (df['short_ma'].iloc[i - 1] > df['long_ma'].iloc[i - 1]):
                # print(f"Sell on: {df['Date'][i]} for {ticker}")
                is_short_below_long_trend = True

        # determine if a buy signal is nearing:
        if (is_short_below_long_trend and is_within_range(df['short_ma'], df['long_ma'], 0.03)
                and is_increasing(df['short_ma'], 30)):
            print("Stock: " + ticker)
            backtesting.back_test(ticker)
            # Plot the moving averages
            # plt.figure(figsize=(10, 6))
            # # plt.plot(df['Date'], df['short_short_ma'], label='15 Day MA')
            # plt.plot(df['Date'], df['short_ma'], label='50 Day MA')
            # plt.plot(df['Date'], df['long_ma'], label='200 Day MA')
            # plt.legend()
            # plt.xlabel('Date')
            # plt.ylabel('Moving Average')
            # plt.title("Stock: " + ticker)
            # plt.show()

    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")

