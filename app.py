"""Streamlit UI for PC Configuration Agent."""
import streamlit as st
from langgraph_agent import PCConfigAgentLangGraph
import json

# Page configuration
st.set_page_config(
    page_title="PC Configuration Agent",
    page_icon="💻",
    layout="wide"
)

# Initialize session state
if "agent" not in st.session_state:
    st.session_state.agent = PCConfigAgentLangGraph()
    st.session_state.messages = []
    st.session_state.previous_state = None

# Header
st.title("💻 PC Configuration Agent")
st.markdown("Build your perfect PC with AI-powered recommendations")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    st.info(f"Model: {st.session_state.agent.llm.model}")
    st.info(f"Provider: Ollama")
    
    st.header("Instructions")
    st.markdown("""
    1. Enter your PC requirements
    2. Get AI-powered recommendations
    3. Provide feedback to refine results
    4. Build your perfect PC!
    """)
    
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.session_state.previous_state = None
        st.session_state.agent.reset()
        st.rerun()

# Main chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Describe your PC requirements...")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Process with agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if st.session_state.previous_state is None:
                result = st.session_state.agent.invoke(user_input)
            else:
                result = st.session_state.agent.handle_feedback(user_input, st.session_state.previous_state)
            
            st.session_state.previous_state = result
            
            # Display response
            response = result["response"]
            st.markdown(response)
            
            # Add to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Show trace if available
            if result.get("trace"):
                with st.expander("🔍 View Agent Trace"):
                    for step in result["trace"]:
                        st.text(f"{step.timestamp} - {step.step_type}: {step.content}")
