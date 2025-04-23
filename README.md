# AI Room Cleanliness Allowance System

An AI-powered system that analyzes children's room cleanliness and automatically processes allowance payments based on the cleanliness score.

## Features

- Uses GPT-4 Vision to analyze room cleanliness
- Provides detailed feedback on room condition
- Automatically calculates and processes allowance payments
- Supports multiple children with individual accounts
- Handles various image formats (JPG, PNG, WEBP)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-room-allowance.git
cd ai-room-allowance
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
1. Analyze the room's cleanliness
2. Calculate the allowance based on the cleanliness score
3. Process the payment to the child's account

## Configuration

You can adjust the following parameters in the `RoomAllowanceAgent` class:
- `cleanliness_threshold`: Minimum score for full allowance (default: 0.7)
- `base_allowance`: Minimum allowance amount (default: $1.00)
- `max_allowance`: Maximum allowance amount (default: $2.00)

## License

MIT License
