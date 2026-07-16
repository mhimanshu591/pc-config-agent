"""Simple test script to verify model text generation."""
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

# Try with a simple direct API call
import google.generativeai as genai

genai.configure(api_key=api_key)

# Try different models to find one with available quota
models_to_try = [
    'gemini-2.5-flash',
    'gemini-2.0-flash-lite',
    'gemini-flash-latest',
    'gemini-pro-latest'
]

for model_name in models_to_try:
    print(f"Testing {model_name}...")
    print("=" * 60)
    
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello! What is 2+2?")
        print(f"Response: {response.text}")
        print("=" * 60)
        print(f"SUCCESS: {model_name} is working!")
        break
    except Exception as e:
        print(f"ERROR with {model_name}: {str(e)[:100]}...")
        print("=" * 60)
        continue
