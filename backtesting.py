import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt


def back_test(ticker):
    # Example ticker
    ticker = ticker
    stock = yf.Ticker(ticker)
    df = stock.history(period="5y")

    # Calculate moving averages
    df['short_ma'] = df['Close'].rolling(window=50).mean()
    df['long_ma'] = df['Close'].rolling(window=200).mean()

    # Identify Golden Cross and Death Cross
    df['golden_cross'] = (df['short_ma'] > df['long_ma']) & (df['short_ma'].shift(1) <= df['long_ma'].shift(1))
    df['death_cross'] = (df['short_ma'] < df['long_ma']) & (df['short_ma'].shift(1) >= df['long_ma'].shift(1))

    # Initialize capital and shares variables
    initial_capital = 10000  # Starting capital
    capital = initial_capital
    shares = 0
    transactions = []  # To track buy/sell points for plotting

    # Simulate trading
    crossover_count = 0
    for date, row in df.iterrows():
        if row['golden_cross'] and capital > 0:
            # Buy
            shares = capital / row['Close']
            capital = 0  # Invest all capital
            transactions.append((date, row['Close'], 'buy'))
            crossover_count += 1
        elif row['death_cross'] and shares > 0:
            # Sell
            capital = shares * row['Close']
            shares = 0
            transactions.append((date, row['Close'], 'sell'))
            crossover_count += 1

    # Calculate final value (considering remaining shares)
    final_value = capital + (shares * df.iloc[-1]['Close'])

    # Plotting
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df['Close'], label='Close Price', alpha=0.5)
    plt.plot(df.index, df['short_ma'], label='50-Day MA', alpha=0.75)
    plt.plot(df.index, df['long_ma'], label='200-Day MA', alpha=0.75)

    # Highlight buy/sell points
    for transaction in transactions:
        if transaction[2] == 'buy':
            plt.scatter(transaction[0], transaction[1], color='green', marker='^', alpha=1)
        else:
            plt.scatter(transaction[0], transaction[1], color='red', marker='v', alpha=1)

    plt.title(f"Backtesting Golden Cross Strategy for {ticker}")
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()


    # Print the final performance
    print(f"Initial Capital: {initial_capital}")
    print(f"Final Value: {final_value}")
    print(f"Net Profit: {final_value - initial_capital}")
    print(f"Crossover Volotility: {crossover_count}")
    plt.show()