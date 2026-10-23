import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY was not loaded.")

client = genai.Client(api_key=api_key)

print("Models available to this API key:")

for model in client.models.list():
    print(model.name)