import os
import boto3
from dotenv import load_dotenv

# Load environment variables from a .env file.
# Expected keys: AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY.
load_dotenv()

# Initialize a DynamoDB resource using AWS credentials and region from environment variables.
dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

# Reference the 'chat_history' DynamoDB table where chat sessions are stored.
table = dynamodb.Table("chat_history")

# Perform a scan operation to retrieve all session IDs.
# Only the 'session_id' attribute is fetched to reduce response size.
response = table.scan(ProjectionExpression="session_id")

# Extract session IDs from the scan result.
session_keys = [item['session_id'] for item in response.get('Items', [])]

# Display the results to the user.
if not session_keys:
    print("No sessions found in DynamoDB.")
else:
    print(f"{len(session_keys)} session(s) found:\n")
    for key in session_keys:
        print(f"- {key}")
