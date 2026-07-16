"""Main entry point for PC Configuration Agent."""
import sys
from langgraph_agent import PCConfigAgentLangGraph


def main():
    """Run the PC Configuration Agent."""
    print("=== PC Configuration Agent (LangGraph) ===\n")
    
    try:
        agent = PCConfigAgentLangGraph()
        
        print("Agent ready. Type 'quit' to exit.\n")
        
        previous_state = None
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Check if this is a new conversation or feedback
            if previous_state is None:
                # First interaction
                print("\nAgent: Processing your request...")
                result = agent.invoke(user_input)
                print(f"\nAgent: {result['response']}")
                previous_state = result
            else:
                # Feedback loop
                print("\nAgent: Processing your feedback...")
                result = agent.handle_feedback(user_input, previous_state)
                print(f"\nAgent: {result['response']}")
                previous_state = result
            
            # Ask if user wants to continue
            continue_chat = input("\nContinue? (yes/no): ").strip().lower()
            if continue_chat not in ['yes', 'y']:
                print("Goodbye!")
                break
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
