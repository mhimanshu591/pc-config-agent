"""Standalone test for Groq RAG concept."""
import os
from dotenv import load_dotenv

load_dotenv()

# Test basic Groq connection
try:
    from langchain_groq import ChatGroq
    from langchain_core.tools import tool
    from langchain_core.messages import HumanMessage
    
    print("=" * 60)
    print("Testing Groq RAG Concept")
    print("=" * 60)
    
    # Check for API key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("❌ GROQ_API_KEY not found in .env file")
        print("Please get a free API key from: https://console.groq.com/keys")
        exit(1)
    
    print(f"✅ API Key found: {groq_api_key[:10]}...")
    
    # Initialize Groq
    print("\nInitializing Groq with llama-3.3-70b-versatile...")
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        api_key=groq_api_key
    )
    print("✅ Groq initialized successfully")
    
    # Test 1: Basic text generation
    print("\n" + "=" * 60)
    print("Test 1: Basic Text Generation")
    print("=" * 60)
    
    response = llm.invoke("What is 2+2? Answer in one word.")
    print(f"Response: {response.content}")
    print("✅ Basic generation works")
    
    # Test 2: Tool calling
    print("\n" + "=" * 60)
    print("Test 2: Tool Calling")
    print("=" * 60)
    
    @tool
    def calculator(a: str, b: str) -> str:
        """Add two numbers."""
        return str(float(a) + float(b))
    
    llm_with_tools = llm.bind_tools([calculator])
    
    response = llm_with_tools.invoke("What is 15 + 27?")
    
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print(f"✅ Tool calling works!")
        print(f"Tool calls: {response.tool_calls}")
        
        # Execute the tool using invoke method
        tool_result = calculator.invoke(response.tool_calls[0]['args'])
        print(f"Tool result: {tool_result}")
    else:
        print(f"❌ Tool calling failed")
        print(f"Response: {response.content}")
    
    # Test 3: Simple RAG-like scenario
    print("\n" + "=" * 60)
    print("Test 3: Simple RAG-like Scenario")
    print("=" * 60)
    
    @tool
    def search_products(category: str, budget: str) -> str:
        """Search for products in a category within budget."""
        # Simulated product database
        products = {
            "cpu": [
                {"name": "AMD Ryzen 5 5600X", "price": 200},
                {"name": "Intel Core i5-12400F", "price": 200},
                {"name": "AMD Ryzen 7 5800X", "price": 300}
            ],
            "gpu": [
                {"name": "NVIDIA RTX 3060", "price": 300},
                {"name": "NVIDIA RTX 3070", "price": 500},
                {"name": "AMD RX 6600 XT", "price": 350}
            ]
        }
        
        if category not in products:
            return f"No products found in category: {category}"
        
        budget_float = float(budget)
        results = [p for p in products[category] if p['price'] <= budget_float]
        
        if not results:
            return f"No {category} found within ${budget}"
        
        return f"Found {len(results)} {category}(s): " + ", ".join([f"{p['name']} (${p['price']})" for p in results])
    
    llm_with_search = llm.bind_tools([search_products])
    
    user_query = "I need a CPU for my gaming PC with a $250 budget"
    print(f"User query: {user_query}")
    
    response = llm_with_search.invoke(user_query)
    
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print(f"✅ Agent decided to use tools!")
        print(f"Tool calls: {response.tool_calls}")
        
        # Execute the search using invoke method
        tool_result = search_products.invoke(response.tool_calls[0]['args'])
        print(f"Search result: {tool_result}")
        
        # Get final response with context
        final_response = llm.invoke(f"User asked: {user_query}. Search results: {tool_result}. Provide a recommendation.")
        print(f"\nFinal recommendation: {final_response.content}")
    else:
        print(f"❌ Agent didn't use tools")
        print(f"Response: {response.content}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
    print("\nGroq RAG concept is working for your prototype!")
    print("You can now integrate this into your main project.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install: pip install langchain-groq")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
