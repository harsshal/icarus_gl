import threading
import time
from ibkr_order import IBOrderManager 
from risk import risk_management 

def main():
    # Start the risk management thread
    risk_thread = threading.Thread(target=risk_management, daemon=False)
    risk_thread.start()

    # Run the order program in the main thread
    order_manager = IBOrderManager('AAPL', 'BUY', 'LMT', 200, 100)
    order_manager.send_order()



if __name__ == "__main__":
    main()
