import logging
from bs4 import BeautifulSoup as bs
import pandas as pd
from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.wrapper import EWrapper
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestApp(EWrapper, EClient):
    def __init__(self, addr, port, client_id):
        EWrapper.__init__(self)
        EClient.__init__(self, self)

        self.firstReqId = 8001
        self.contract = None  # For storing the single contract
        self.fundamental_data_received = False  # Flag to indicate data reception

        # DataFrame to store balance sheet data
        self.df_balance_sheet = pd.DataFrame()

        logger.info("TestApp initialized.")

    def addContract(self, cont):
        logger.info(f"Adding contract: {cont.symbol}")
        self.contract = cont

    def nextValidId(self, orderId: int):
        logger.info(f"Received next valid order ID: {orderId}. Requesting balance sheet data.")
        # Request balance sheet data for Apple using "ReportsFinSummary"
        self.reqFundamentalData(self.firstReqId, self.contract, "ReportsFinSummary", [])

    def error(self, reqId, errorCode, errorString):
        logger.error(f"Error for request {reqId}: {errorCode} - {errorString}")
        self.disconnect()

    def fundamentalData(self, reqId, fundamental_data):
        logger.info(f"Received fundamental data for request {reqId}.")
        try:
            if fundamental_data is not None:
                # Parse the fundamental data and extract the balance sheet
                self.df_balance_sheet = self.parseFundamentalData(fundamental_data)
                logger.info("Balance sheet data added to DataFrame.")
                # After receiving the data, disconnect from IBKR
                self.disconnect()
        except Exception as e:
            logger.error(f"Failed to parse balance sheet data: {e}")
            self.disconnect()

    def parseFundamentalData(self, fundamentals):
        """Extracts balance sheet data from the XML and returns it as a DataFrame."""
        soup = bs(fundamentals, 'xml')

        # Prepare lists to hold balance sheet data
        balance_sheet_data = []

        for period in soup.find_all('FiscalPeriod'):
            # Extract fiscal period type
            period_type = period.get('Type')

            for statement in period.find_all('Statement'):
                if statement.get('Type') == 'BAL':  # Only extract Balance Sheet data
                    balance_sheet = {}
                    balance_sheet['rep_date'] = statement.find('StatementDate').text
                    balance_sheet['period_type'] = period_type

                    for lineItem in statement.find_all('lineItem'):
                        line_code = lineItem.get('coaCode')
                        line_value = lineItem.text
                        balance_sheet[line_code] = line_value

                    balance_sheet_data.append(balance_sheet)

        # Create DataFrame from the list of balance sheet data
        df_balance_sheet = pd.DataFrame(balance_sheet_data)
        return df_balance_sheet

def main():
    logger.info("Main process started.")

    # Set up the path to save the CSV file
    project_data_folder = Path('C:/Users/starf/OneDrive/Desktop/icarus')
    if not project_data_folder.exists():
        project_data_folder.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created data folder: {project_data_folder}")

    client = TestApp('127.0.0.1', 7497, 0)
    client.connect('127.0.0.1', 7497, 0)

    # Define the contract for Apple (AAPL)
    contract = Contract()
    contract.symbol = 'AAPL'
    contract.secType = 'STK'
    contract.currency = 'USD'
    contract.exchange = "SMART"

    logger.info("Adding contract for AAPL.")
    client.addContract(contract)

    logger.info("Running client.")
    client.run()

    # File name where the balance sheet data will be saved
    balance_sheet_file_name = 'apple_balance_sheet.csv'
    file_name = project_data_folder / balance_sheet_file_name

    # Always create a CSV file, even if the dataframe is empty
    try:
        if not client.df_balance_sheet.empty:
            # Save the data to a CSV file if available
            client.df_balance_sheet.to_csv(file_name, index=False)
            logger.info(f"Balance sheet data saved to {file_name}")
        else:
            # Create an empty CSV file with headers if no data is received
            pd.DataFrame().to_csv(file_name, index=False)
            logger.warning(f"No data received. Created an empty CSV file: {file_name}")
    except Exception as e:
        logger.error(f"Error saving balance sheet data: {e}")

    logger.info("Main process finished.")


if __name__ == "__main__":
    main()
