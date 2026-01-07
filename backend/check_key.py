
from config import settings
import os

print(f"Checking API Key configuration...")
key = settings.GROQ_API_KEY

if not key:
    print("❌ GROQ_API_KEY is missing or empty!")
    print("Please check your .env file.")
else:
    print(f"✅ GROQ_API_KEY found (Length: {len(key)})")
    if key.startswith("gsk_"):
        print("✅ Key format looks correct (starts with gsk_)")
    else:
        print("⚠️ Key format warning: Does not start with 'gsk_'")
