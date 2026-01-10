import redis

# Initialize a Redis client using a local Redis server.
# This client will be used to query stored chat session keys.
redis_client = redis.Redis.from_url("redis://localhost:6379")

# Retrieve all Redis keys that match the pattern 'session_*'.
# These keys represent stored chat sessions.
keys = redis_client.keys("session_*")

# Decode byte keys to UTF-8 string format for readability.
session_keys = [key.decode("utf-8") for key in keys]

# Check if any session keys were found and display them.
if not session_keys:
    print("No sessions found in Redis.")
else:
    print(f"{len(session_keys)} session(s) found:\n")
    for key in session_keys:
        print(f"- {key}")
