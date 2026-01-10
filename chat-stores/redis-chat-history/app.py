import os
import uuid
from dotenv import load_dotenv
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.storage.chat_store.redis import RedisChatStore
from llama_index.llms.ollama import Ollama
import redis

# 1. Load environment variables from a .env file.
# This typically includes secrets or configuration variables (e.g., database passwords).
load_dotenv()

# 2. Establish a connection to a local Redis server.
# Redis is used as the backend chat store for storing conversation history.
redis_client = redis.Redis.from_url("redis://localhost:6379")
redis_chat_store = RedisChatStore(redis_client=redis_client)

# 3. Initialize a local LLM using Ollama.
# Replace "gemma3n" with the model name installed on your system.
llm = Ollama(model="gemma3n")

# 4. Generate a unique chat session key using UUID.
# This key will be used to store and retrieve chat history from Redis.
chat_store_key = f"session_{uuid.uuid4()}"

# 5. Create a chat memory buffer that stores messages in Redis.
# This buffer maintains the conversation context up to a specified token limit.
memory = ChatMemoryBuffer.from_defaults(
    chat_store=redis_chat_store,
    chat_store_key=chat_store_key,
    token_limit=3000
)

# 6. Create a simple chat engine with the configured LLM and memory.
# The system prompt defines the assistant's behavior and tone.
chat_engine = SimpleChatEngine.from_defaults(
    llm=llm,
    memory=memory,
    system_prompt="You are a knowledgeable assistant who answers based on your own information. The conversation is stored in Redis."
)

# 7. Interactive chat loop
# Accepts user input, sends it to the LLM, and prints the response.
# Press Ctrl+C to terminate the session.
print(f"Chat engine is ready! (Session key: {chat_store_key})")
print("Press Ctrl+C to exit\n")

while True:
    try:
        user_input = input("User: ")
        response = chat_engine.chat(user_input)
        print(f"Assistant: {response}")
    except KeyboardInterrupt:
        print("\nChat session terminated.")
        break
