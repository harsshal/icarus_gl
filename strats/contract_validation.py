# https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/#request-contract-details
from time import sleep
import hputils

from ibkr_base import IBBase

class ContractValidation(IBBase):
    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker

    def start(self):
        #self.reqContractDetails(1, self.create_contract(self.ticker))
        self.reqMatchingSymbols(1, self.ticker)
        sleep(1)
        self.disconnect_client()

    def symbolSamples(self, reqId: int, contractDescriptions):
        super().symbolSamples(reqId, contractDescriptions)
        print(f"Symbol Samples. Request Id: {reqId}")

        for contractDescription in contractDescriptions:
            contract = contractDescription.contract
            derivSecTypes = " ".join(contractDescription.derivativeSecTypes)
            print(
                f"Contract: conId:{contract.conId}, "
                f"symbol:{contract.symbol}, "
                f"secType:{contract.secType}, "
                f"primExchange:{contract.primaryExchange}, "
                f"currency:{contract.currency}, "
                f"derivativeSecTypes:{derivSecTypes}, "
            )


def main():
    app = ContractValidation("TIGR")
    app.run_client()  # Correctly run the client

if __name__ == "__main__":
    main()
