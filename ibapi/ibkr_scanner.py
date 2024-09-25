import pandas as pd
from ibapi.scanner import ScannerSubscription
from ibapi.tag_value import TagValue
from ibapi.contract import ContractDetails
from ibkr_base import IBBase
from time import sleep

class IBScanner(IBBase):
    def __init__(self, scancode, tagvalues):
        super().__init__()
        self.data = []
        self.scancode = scancode
        self.tagvalues = tagvalues

    def start(self):
        scan_sub = ScannerSubscription()
        scan_sub.instrument = "STK"
        scan_sub.locationCode = "STK.US.MAJOR"
        scan_sub.scanCode = self.scancode  # More relevant for volume and momentum

        self.reqScannerSubscription(7001, scan_sub, [], self.tagvalues)
        sleep(1)
        self.cancelScannerSubscription(7001)

    def scannerData(self, reqId: int, rank: int, contractDetails: ContractDetails, 
                    distance: str, benchmark: str, projection: str, legsStr: str):
        new_data = {
            'rank': rank,
            'contract': contractDetails.contract.symbol,
            'distance': distance,
            'benchmark': benchmark,
            'projection': projection,
            'legsStr': legsStr
        }
        self.data.append(new_data)

    def scannerDataEnd(self, reqId: int):
        print(f"ScannerDataEnd. ReqId: {reqId}")
        self.disconnect_client()

    def get_scanner_data(self):
        return pd.DataFrame(self.data)


def get_ibkr_scanner(scancode, tagvalues):
    app = IBScanner(scancode, tagvalues)
    app.run_client()
    return app.get_scanner_data()


def main():
    # Adding the required filters
    scancode = "TOP_VOLUME_RATE"

    tagvalues = [
        # TagValue("priceAbove", "1"),         # Price above $1
        # TagValue("priceBelow", "20"),        # Price below $20
        # TagValue("percentChangeAbove", "10"),  # Up at least 10%
        # TagValue("relVolumeAbove", "5"),     # Relative volume 5x normal
        # TagValue("marketCapBelow", "20000000"),  # Market cap below 20 million shares
        # TagValue("scannerSettingPairs", "news"),  # Breaking news
        # TagValue("changeAbove", "0")         # To capture momentum (moving quickly)
    ]
    
    df = get_ibkr_scanner(scancode, tagvalues)
    if not df.empty:
        print(df)
    else:
        print("No data received.")


if __name__ == "__main__":
    main()
