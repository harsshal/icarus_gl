import time

def risk_management():
    check_count = 0 
    max_checks = 5   

    while check_count < max_checks:
        print(f"Performing risk management check {check_count + 1}...")
        time.sleep(1)  # Perform checks every 1 second
        check_count += 1 

    print("Risk management checks completed.")
