import pandas as pd
from ibapi.scanner import ScannerSubscription
from ibapi.tag_value import TagValue
from ibapi.contract import ContractDetails
from ibkr_base import IBBase
from time import sleep


class IBScanner(IBBase):
    def __init__(self):
        super().__init__()
        self.data = []

    def start(self):
        scan_sub = ScannerSubscription()
        scan_sub.instrument = "STK"
        scan_sub.locationCode = "STK.US.MAJOR"
        scan_sub.scanCode = "TOP_PERC_GAIN"

        tagvalues = [TagValue("optVolumeAbove", "10000"),
                     TagValue("avgVolumeAbove", "100000"),
                     TagValue("priceAbove", "1")]

        self.reqScannerSubscription(7001, scan_sub, [], tagvalues)
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


def get_ibkr_scanner():
    app = IBScanner()
    app.run_client()
    return app.get_scanner_data()


def main():
    df = get_ibkr_scanner()
    if not df.empty:
        print(df)
    else:
        print("No data received.")


if __name__ == "__main__":
    main()
