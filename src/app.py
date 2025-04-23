from paymanai import Paymanai
import os
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

def main():
    try:
        # Initialize Paymanai client
        payman = Paymanai(
            x_payman_api_secret=os.getenv("PAYMAN_API_SECRET")
        )

        # Check available balance
        balance = payman.balances.get_spendable_balance("TSD")
        print(f"Available balance: ${balance:.2f}")

        # Generate a unique identifier for the test payee
        unique_id = str(uuid.uuid4())[:8]

        # Create a payee with unique details
        payee = payman.payments.create_payee(
            type="TEST_RAILS",
            name=f"Test Account {unique_id}",
            tags=["test", "sandbox", f"test_{unique_id}"]
        )

        # Send payment
        payment = payman.payments.send_payment(
            amount_decimal=20.00,
            payee_id=payee.id,
            memo="Test payment"
        )

        print("Payee created:", payee)
        print("Payment created:", payment)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
