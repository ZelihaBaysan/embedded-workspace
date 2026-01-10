import redis
import os
from dotenv import load_dotenv

# Load environment variables from a .env file.
# Typically includes secrets or configurations needed for external services.
load_dotenv()

# Initialize a Redis client using a local Redis server.
# The connection string can be updated in the .env file if needed.
redis_client = redis.Redis.from_url("redis://localhost:6379")

# Prompt the user to enter the Redis session key corresponding to the chat history.
# Example: session_1, session_abcd1234, etc.
chat_store_key = input("Enter the session key you want to retrieve (e.g., session_1): ")

# Retrieve the full list of chat messages stored under the given Redis list key.
chat_list = redis_client.lrange(chat_store_key, 0, -1)

# If the list is empty or the key does not exist, notify the user.
if not chat_list:
    print(f"No records found for session key: {chat_store_key}")
else:
    # Write the retrieved chat messages to a local text file.
    # The output file is named 'redis_chat_history.txt' and encoded in UTF-8.
    with open("redis_chat_history.txt", "w", encoding="utf-8") as f:
        f.write(f"CHAT HISTORY ({chat_store_key})\n")
        f.write("-" * 50 + "\n")
        for msg in chat_list:
            decoded = msg.decode("utf-8")  # Decode byte strings into readable text
            f.write(decoded + "\n")
    print("Chat history has been written to 'redis_chat_history.txt'.")
