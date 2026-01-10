import os
import boto3
from dotenv import load_dotenv

# Load environment variables from a .env file.
# Expected variables include AWS_REGION, AWS_ACCESS_KEY_ID, and AWS_SECRET_ACCESS_KEY.
load_dotenv()

# Initialize a DynamoDB resource using credentials and region from environment variables.
dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

# Reference the 'chat_history' table where chat sessions are stored.
table = dynamodb.Table("chat_history")

# Prompt the user to enter the session key whose chat history is to be retrieved.
# Example input: session_1, session_abc123, etc.
chat_store_key = input("Enter the session key you want to retrieve (e.g., session_1): ")

# Query DynamoDB for the item matching the given session ID.
response = table.get_item(Key={'session_id': chat_store_key})

# Check if a record exists for the specified session ID.
if 'Item' not in response:
    print(f"No records found for session key: {chat_store_key}")
else:
    # Extract the chat history from the item, defaulting to an empty list if not present.
    chat_history = response['Item'].get('history', [])

    # If no chat messages are stored under the session key.
    if not chat_history:
        print(f"No chat history found for session key: {chat_store_key}")
    else:
        # Write the chat history to a text file in UTF-8 encoding.
        with open("dynamodb_chat_history.txt", "w", encoding="utf-8") as f:
            f.write(f"CHAT HISTORY ({chat_store_key})\n")
            f.write("-" * 50 + "\n")
            for msg in chat_history:
                f.write(msg + "\n")
        print("Chat history has been written to 'dynamodb_chat_history.txt'.")
