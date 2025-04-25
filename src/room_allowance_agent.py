from paymanai import Paymanai
import os
from dotenv import load_dotenv
import uuid
import base64
import requests
from datetime import datetime
import json
import re

class RoomAllowanceAgent:
    def __init__(self, api_secret):
        self.payman = Paymanai(x_payman_api_secret=api_secret)
        self.cleanliness_threshold = 0.7  # Minimum score for full allowance
        self.base_allowance = 1.00  # Base allowance amount
        self.max_allowance = 2.00   # Maximum allowance amount
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.webp']
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
    def validate_image(self, image_path):
        """
        Validate if the image file exists and is in a supported format
        """
        if not os.path.exists(image_path):
            raise ValueError(f"Image file not found: {image_path}")
            
        file_ext = os.path.splitext(image_path)[1].lower()
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported image format: {file_ext}. Supported formats: {', '.join(self.supported_formats)}")
            
        return True

    def encode_image(self, image_path):
        """
        Encode image to base64 for GPT-4V API
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def clean_json_response(self, content):
        """
        Clean the response content by removing markdown formatting
        """
        # Remove markdown code block markers
        content = re.sub(r'^```json\n', '', content)
        content = re.sub(r'\n```$', '', content)
        return content.strip()

    def analyze_room_cleanliness(self, image_path):
        """
        Analyze the cleanliness of a room using GPT-4 Vision
        Returns a score between 0 and 1
        """
        try:
            # Validate image
            self.validate_image(image_path)
            
            # Encode image
            base64_image = self.encode_image(image_path)
            
            # Prepare the API request
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_api_key}"
            }
            
            payload = {
                "model": "gpt-4o",  # Current model name (gpt-4-vision-preview is deprecated)
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this room's cleanliness and provide a score between 0 and 1. 
                                Consider:
                                1. Overall tidiness
                                2. Presence of clutter
                                3. Bed making
                                4. Floor cleanliness
                                5. Organization of items
                                
                                Respond with a JSON object containing:
                                {
                                    "score": float between 0 and 1,
                                    "explanation": "detailed explanation of the score",
                                    "specific_observations": ["list of specific observations"]
                                }"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 500
            }
            
            #print("\nSending request to OpenAI API...")
            
            # Make the API request
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                print(f"API Error Response: {response.text}")
                raise Exception(f"OpenAI API error: {response.text}")
            
            # Parse the response
            result = response.json()
            #print(f"\nRaw API Response: {json.dumps(result, indent=2)}")
            
            if 'choices' not in result or not result['choices']:
                raise Exception("No choices in API response")
                
            content = result['choices'][0]['message']['content']
            #print(f"\nRaw Content: {content}")
            
            # Clean the content before parsing JSON
            cleaned_content = self.clean_json_response(content)
            #print(f"\nCleaned Content: {cleaned_content}")
            
            try:
                analysis = json.loads(cleaned_content)
                #print(f"\nParsed Analysis: {json.dumps(analysis, indent=2)}")
            except json.JSONDecodeError as e:
                #print(f"Failed to parse JSON from content: {cleaned_content}")
                raise Exception(f"Invalid JSON response: {str(e)}")
            
            if not isinstance(analysis, dict) or 'score' not in analysis:
                raise Exception("Invalid analysis format: missing required fields")
            
            #print("\nRoom Analysis:")
            #print(f"Score: {analysis['score']:.2f}")
            #print(f"Explanation: {analysis['explanation']}")
            #print("\nSpecific Observations:")
            #for obs in analysis['specific_observations']:
            #    print(f"- {obs}")
            
            return analysis
            
        except Exception as e:
            #print(f"Error analyzing room: {str(e)}")
            return None

    def calculate_allowance(self, cleanliness_score):
        """
        Calculate allowance based on cleanliness score
        """
        if cleanliness_score >= self.cleanliness_threshold:
            return self.max_allowance
        else:
            # Linear scaling between 0 and base_allowance
            return self.base_allowance * (cleanliness_score / self.cleanliness_threshold)

    def get_or_create_payee(self, child_name):
        """
        Get existing payee or create a new one
        """
        try:
            # Search for existing payee
            #print(f"\nSearching for payee with name: {child_name}")
            payees = self.payman.payments.search_payees(
                name=child_name
            )
            
            #print(f"Search results: {payees}")
            
            # Parse the search results if it's a string
            if isinstance(payees, str):
                try:
                    payees = json.loads(payees)
                except json.JSONDecodeError as e:
                    print(f"Failed to parse payees JSON: {str(e)}")
                    return self.create_new_payee(child_name)
            
            # Validate search results
            if not payees or not isinstance(payees, list):
                print("No valid payees found, creating new payee")
                return self.create_new_payee(child_name)
                
            if len(payees) == 0:
                print("No payees found, creating new payee")
                return self.create_new_payee(child_name)
                
            # Get the first payee from the list
            first_payee = payees[0]
            if isinstance(first_payee, dict) and 'id' in first_payee:
                #print(f"Found existing payee with ID: {first_payee['id']}")
                return first_payee
            else:
                #print(f"Invalid payee format: {first_payee}, creating new payee")
                return self.create_new_payee(child_name)
            
        except Exception as e:
            print(f"Error in get_or_create_payee: {str(e)}")
            raise
            
    def create_new_payee(self, child_name):
        """
        Create a new payee
        """
        #print(f"Creating new payee for {child_name}")
        new_payee = self.payman.payments.create_payee(
            type="TEST_RAILS",
            name=child_name,
            tags=["allowance", "child", child_name.lower()]
        )
        print(f"Created new payee: {new_payee}")
        return new_payee

    def process_room_and_pay(self, image_path, child_name):
        """
        Process a room image and make allowance payment
        """
        try:
            # Analyze room cleanliness
            analysis = self.analyze_room_cleanliness(image_path)
            if not analysis:
                return None
                
            #print(f"\nCleanliness score: {analysis['score']:.2f}")
            
            # Calculate allowance
            allowance_amount = self.calculate_allowance(analysis['score'])
            #print(f"Allowance amount: ${allowance_amount:.2f}")
            
            # Get or create payee
            payee = self.get_or_create_payee(child_name)
            #print(f"Using payee: {payee}")
            
            # Get payee ID based on the type of payee object
            if isinstance(payee, dict):
                payee_id = payee["id"]
            else:
                payee_id = payee.id
                
            # Send payment
            payment = self.payman.payments.send_payment(
                amount_decimal=allowance_amount,
                payee_id=payee_id,
                memo=f"Allowance for {child_name} - Room Cleanliness Score: {analysis['score']:.2f}"
            )
            
            return {
                "cleanliness_score": analysis['score'],
                "allowance_amount": allowance_amount,
                "payment": payment,
                "explanation": analysis['explanation'],
                "specific_observations": analysis['specific_observations']
            }
            
        except Exception as e:
            #print(f"Error processing room and payment: {str(e)}")
            return None

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize the agent
    agent = RoomAllowanceAgent(os.getenv("PAYMAN_API_SECRET"))
    
    # Example usage
    image_path = "/Users/Amias/Desktop/kids-room-after-tag.webp"  # Replace with actual image path
    child_name = "Susie"
    
    result = agent.process_room_and_pay(image_path, child_name)
    #print(f"Result: {result}")

if __name__ == "__main__":
    main() 