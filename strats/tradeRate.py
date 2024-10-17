from ibkr_scanner import get_ibkr_scanner
from ibkr_data import get_ibkr_data
from ibapi.tag_value import TagValue
from time import sleep
import utils


def main():
    # Fetch the top 50 high volume rates using the scanner
    tagvalues = [
        # TagValue("priceAbove", "1"),         # Price above $1
        # TagValue("priceBelow", "20"),        # Price below $20
        # TagValue("percentChangeAbove", "10"),  # Up at least 10%
        # TagValue("relVolumeAbove", "5"),     # Relative volume 5x normal
        # TagValue("marketCapBelow", "20000000"),  # Market cap below 20 million shares
        # TagValue("scannerSettingPairs", "news"),  # Breaking news
        # TagValue("changeAbove", "0")         # To capture momentum (moving quickly)
        TagValue("tradeRateAbove", "100"),       # trades per min
    ]

    df_scanner = get_ibkr_scanner("TOP_PERC_GAIN", tagvalues)

    if df_scanner.empty:
        print("No stocks found from the scanner.")
        return

    # Loop through the top 50 stocks provided by the scanner
    for _, row in df_scanner[:5].iterrows():
        ticker = row['contract']
        print(f"Running strategy for {ticker}")
        # Apply the strategy to each stock
        ticker_data = get_ibkr_data(ticker, '', '100 S', '1 secs')
        print(ticker_data)
        if len(ticker_data) > 0:
            mometum_price = utils.momentum_price(ticker_data[:-10]['Close'])
            print(mometum_price)
        sleep(1)


if __name__ == "__main__":
    main()