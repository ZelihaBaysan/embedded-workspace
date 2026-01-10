import os
import uuid
import boto3
from dotenv import load_dotenv
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage

# Load environment variables from a .env file.
# This includes AWS credentials and region configuration.
load_dotenv()

# Initialize a DynamoDB resource using AWS credentials.
# Make sure the credentials and region are correctly set in the environment.
dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

# Reference the 'chat_history' table in DynamoDB.
table = dynamodb.Table("chat_history")

# Initialize the local language model (LLM) using Ollama.
# Replace 'gemma3n' with the model name available on your system.
llm = Ollama(model="gemma3n")

# Generate a unique session ID for tracking chat sessions.
session_id = f"session_{uuid.uuid4()}"
print(f"Chat engine is ready! (Session key: {session_id})")
print("Press Ctrl+C to exit\n")

# Initialize an in-memory list to store the chat history.
chat_history = []

# Start the chat loop:
# - Accepts user input
# - Sends the message to the LLM
# - Stores the conversation in DynamoDB
while True:
    try:
        user_input = input("User: ")
        chat_history.append(f"User: {user_input}")

        # Create a ChatMessage object for the user's input.
        message = ChatMessage(role="user", content=user_input)

        # Send the message to the LLM and retrieve the assistant's response.
        response = llm.chat(messages=[message])
        assistant_reply = response.message.content

        print(f"Assistant: {assistant_reply}")
        chat_history.append(f"Assistant: {assistant_reply}")

        # Persist the updated chat history to DynamoDB after each interaction.
        table.put_item(
            Item={
                'session_id': session_id,
                'history': chat_history
            }
        )

    except KeyboardInterrupt:
        print("\nChat session terminated.")
        break
