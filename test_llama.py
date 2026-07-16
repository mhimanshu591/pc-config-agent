"""Test script for tool calling support."""
import os
from dotenv import load_dotenv

load_dotenv()

# Test tool calling support with different models
try:
    from langchain_ollama import ChatOllama
    from langchain_core.tools import tool
    
    print("Testing tool calling support...")
    print("=" * 60)
    
    @tool
    def calculator(a: str, b: str) -> str:
        """Add two numbers."""
        return str(float(a) + float(b))
    
    # Try different models known to support tools
    models_to_try = ["phi3", "llama3", "mistral", "gemma2:2b"]
    
    for model_name in models_to_try:
        print(f"\nTrying {model_name}...")
        try:
            llm = ChatOllama(model=model_name, temperature=0.7)
            llm_with_tools = llm.bind_tools([calculator])
            
            # Test tool calling
            response = llm_with_tools.invoke("What is 5 + 3?")
            
            if hasattr(response, 'tool_calls') and response.tool_calls:
                print(f"✓ {model_name} supports tool calling!")
                print(f"  Tool calls: {response.tool_calls}")
                print("=" * 60)
                print(f"SUCCESS: {model_name} is ready for the agent!")
                break
            else:
                print(f"✗ {model_name} does not support tool calling")
                print(f"  Response: {response.content[:100]}...")
        except Exception as e:
            print(f"✗ Error with {model_name}: {str(e)[:100]}...")
    
except ImportError:
    print("langchain-ollama not installed")
except Exception as e:
    print(f"ERROR: {e}")
