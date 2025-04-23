# AI Room Cleanliness Allowance System

An AI-powered system that analyzes children's room cleanliness and automatically processes allowance payments using the [Payman API](https://payman.ai). This project demonstrates how to integrate Payman's payment processing capabilities with AI-powered room analysis.

## Features

- Uses GPT-4 Vision to analyze room cleanliness
- Integrates with [Payman API](https://payman.ai) for seamless payment processing
- Provides detailed feedback on room condition
- Automatically calculates and processes allowance payments
- Supports multiple children with individual Payman accounts
- Handles various image formats (JPG, PNG, WEBP)

## Payman Integration

This project uses Payman's API for payment processing. Key Payman features used:
- Payee management
- Payment processing
- Balance checking
- Test/sandbox environment support

To use Payman in your own projects:
1. Sign up for a Payman account at [payman.ai](https://payman.ai)
2. Get your API key from the Payman dashboard
3. Use the Payman Python SDK or REST API for integration

## Setup

1. Clone the repository:
```bash
git clone https://github.com/amiasmg/ai-payment-tool.git
cd ai-payment-tool
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:
```
PAYMAN_API_SECRET=your_payman_api_secret
OPENAI_API_KEY=your_openai_api_key
```

## Usage

Run the script with an image of a child's room:
```bash
python src/room_allowance_agent.py
```

The system will:
1. Analyze the room's cleanliness using GPT-4 Vision
2. Calculate the allowance based on the cleanliness score
3. Process the payment through Payman to the child's account

## Payman API Examples

Here are some examples of how to use the Payman API in this project:

```python
# Initialize Payman client
payman = Paymanai(x_payman_api_secret=os.getenv("PAYMAN_API_SECRET"))

# Create a payee
payee = payman.payments.create_payee(
    type="TEST_RAILS",
    name="Child Name",
    tags=["allowance", "child"]
)

# Send payment
payment = payman.payments.send_payment(
    amount_decimal=10.00,
    payee_id=payee.id,
    memo="Allowance payment"
)

# Check balance
balance = payman.balances.get_spendable_balance("USD")
```

## Configuration

You can adjust the following parameters in the `RoomAllowanceAgent` class:
- `cleanliness_threshold`: Minimum score for full allowance (default: 0.7)
- `base_allowance`: Minimum allowance amount (default: $1.00)
- `max_allowance`: Maximum allowance amount (default: $2.00)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

MIT License

## Acknowledgments

- [Payman](https://payman.ai) for their excellent payment processing API
- OpenAI for GPT-4 Vision capabilities
