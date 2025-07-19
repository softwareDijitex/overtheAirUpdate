import os
from dotenv import load_dotenv

print("Before load_dotenv():")
print(f"MONGO_URI: {os.environ.get('MONGO_URI')}")

# Load .env file
load_dotenv()

print("\nAfter load_dotenv():")
print(f"MONGO_URI: {os.environ.get('MONGO_URI')}")

# Check if .env file exists and its contents
if os.path.exists('.env'):
    print("\n.env file exists")
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('MONGO_URI'):
                print(f"MONGO_URI in .env: {line.strip()}")
else:
    print("\n.env file does not exist") 