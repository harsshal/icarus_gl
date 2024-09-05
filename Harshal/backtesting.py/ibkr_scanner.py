from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.scanner import ScannerSubscription
from ibapi.tag_value import TagValue
from ibapi.contract import ContractDetails
import pandas as pd
import time

class IBApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = []  # List to accumulate data

    def nextValidId(self, orderId):
        self.start()

    def start(self):
        # Scanner Subscription
        scan_sub = ScannerSubscription()
        scan_sub.instrument = "STK"
        scan_sub.locationCode = "STK.US.MAJOR"
        scan_sub.scanCode = "HOT_BY_VOLUME"

        # Generic Filters
        tagvalues = []
        tagvalues.append(TagValue("optVolumeAbove", "1000"))
        tagvalues.append(TagValue("avgVolumeAbove", "10000"))

        self.reqScannerSubscription(7001, scan_sub, [], tagvalues)
        print("Scanner subscription requested.")
        time.sleep(5)
        self.cancelScannerSubscription(7001)
        print("Scanner subscription canceled.")

    def scannerData(self, reqId: int, rank: int, contractDetails: ContractDetails, distance: str, benchmark: str, projection: str, legsStr: str):
        new_data = {
            'rank': rank,
            'contract': contractDetails.contract.symbol,
            'distance': distance,
            'benchmark': benchmark,
            'projection': projection,
            'legsStr': legsStr
        }
        self.data.append(new_data)
        print(f"Received scanner data: {new_data}")

    def scannerParameters(self, xml: str):
        with open('log/scanner.xml', 'w') as file:
            file.write(xml)
        print("ScannerParameters received.")

    def scannerDataEnd(self, reqId: int):
        print(f"ScannerDataEnd. ReqId: {reqId}")
        self.disconnect()

def get_ibkr_scanner():
    app = IBApi()
    app.connect('127.0.0.1', 7497, 0)

    # Run the socket until data collection is complete
    app.run()

    # Convert the collected data to a DataFrame
    df = pd.DataFrame(app.data)
    return df

def main():
    df = get_ibkr_scanner()
    print(df)

if __name__ == "__main__":
    main()
