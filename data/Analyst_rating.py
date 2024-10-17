from ib_insync import *
import xml.etree.ElementTree as ET

# Function to fetch fundamental data, save XML, and parse analyst ratings
def fetch_and_parse_analyst_ratings(symbol):
    # Initialize the IB client
    ib = IB()

    # Connect to IBKR TWS or Gateway (use appropriate port, clientId)
    ib.connect('127.0.0.1', 7497, clientId=132)

    # Define the contract for the stock (e.g., AAPL for Apple)
    contract = Stock(symbol, 'SMART', 'USD')

    # Request the fundamental data (ReportSnapshot can contain ratings)
    try:
        fundamental_data = ib.reqFundamentalData(contract, 'ReportSnapshot')

        if fundamental_data:
            # Save the XML data to a file
            file_name = f'{symbol}_fundamental_data.xml'
            with open(file_name, 'w') as file:
                file.write(fundamental_data)
            print(f"Fundamental data for {symbol} saved to {file_name}")
            
            # Parse the XML data to extract analyst ratings
            root = ET.fromstring(fundamental_data)
            consensus_rating = None

            # Look for the consensus recommendation field
            for ratio in root.findall(".//Ratio[@FieldName='ConsRecom']"):
                consensus_rating = ratio.find('Value').text
            
            if consensus_rating:
                print(f"Analyst Consensus Rating for {symbol}: {consensus_rating}")
            else:
                print(f"No analyst rating found for {symbol}.")
        else:
            print(f"No fundamental data found for {symbol}.")
    except Exception as e:
        print(f"Error fetching data: {e}")
    finally:
        # Disconnect after retrieving the data
        ib.disconnect()

# Example usage: Fetch and parse the analyst ratings for Apple (AAPL)
fetch_and_parse_analyst_ratings('AAPL')
