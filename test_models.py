#!/usr/bin/env python3
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# List available models
print("Testing Gemini Model Access...")
print("=" * 50)

# Try different model names
model_names = [
    "gemini-pro",
    "gemini-1.5-pro",
    "gemini-1.5-flash", 
    "gemini-1.5-flash-latest",
    "gemini-2.0-flash-exp"
]

for model_name in model_names:
    try:
        print(f"\nTrying: {model_name}")
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0
        )
        response = llm.invoke("Say hello")
        print(f"✅ {model_name} works!")
        print(f"Response: {response.content[:100]}")
        break
    except Exception as e:
        print(f"❌ {model_name}: {str(e)[:100]}")
