# Assignment Requirements Mapping

This document maps the assignment requirements to the implementation files.

## Task 1: Agent Architecture & Design

### Define the agent's goal, available tools, and decision-making flow
- **File**: `langgraph_agent.py`
- **Implementation**: 
  - `PCConfigAgentLangGraph` class defines agent goal (PC configuration assistance)
  - `ToolRegistry` in `tools.py` defines available tools
  - LangGraph workflow in `_build_graph()` defines decision-making flow

### Create an architecture diagram
- **File**: `README.md`
- **Implementation**: ASCII art diagram showing LangGraph workflow, tools, and LLM integration

### Implement the agent loop: reason → plan → act → observe → respond
- **File**: `langgraph_agent.py`
- **Implementation**: 
  - `_agent_node()`: Reasoning with LLM
  - `_tool_executor_node()`: Acting with tools
  - State management: Observing results
  - Response generation: Final output

### Handle at least one tool/function call
- **File**: `tools.py`, `langgraph_agent.py`
- **Implementation**: 
  - Three tools defined: `search_components`, `get_component_types`, `get_component_schema`
  - Tool calling via LangChain's `bind_tools()` method
  - Tool execution in `_tool_executor_node()`

## Task 2: Prompt Engineering & LLM Integration

### Write well-structured system prompts and few-shot examples
- **File**: `prompts.py`
- **Implementation**:
  - `SYSTEM_PROMPT`: Clear role definition and compatibility rules
  - `REQUIREMENT_GATHERING_PROMPT`: Structured requirement collection
  - `FEW_SHOT_EXAMPLES`: Example conversations for guidance

### Handle requirement gathering and ambiguity thoughtfully
- **File**: `prompts.py`, `langgraph_agent.py`
- **Implementation**:
  - System prompt instructs to ask clarifying questions
  - Agent handles incomplete information gracefully
  - Few-shot examples show proper requirement gathering

### Implement structured output parsing
- **File**: `tools.py`, `langgraph_agent.py`
- **Implementation**:
  - Tool schemas define structured inputs
  - JSON-based tool results
  - LangChain's structured output parsing via tool calling

### Demonstrate at least one advanced technique
- **File**: `prompts.py`, `langgraph_agent.py`
- **Implementation**: Chain-of-Thought prompting
  - `CHAIN_OF_THOUGHT_TEMPLATE`: Structured reasoning template
  - Agent uses step-by-step reasoning for component selection
  - Self-reflection capability (though simplified in final version)

## Task 3: Robustness & Error Handling

### Query and reason over the dataset effectively
- **File**: `data_loader.py`, `tools.py`
- **Implementation**:
  - `ComponentDataLoader` loads and indexes CSV data
  - `search_components` tool with filtering capabilities
  - Efficient pandas-based queries

### Recommend conceptually compatible PC configurations
- **File**: `prompts.py`, `langgraph_agent.py`
- **Implementation**:
  - System prompt includes compatibility rules
  - Agent trained to check socket, form factor, power requirements
  - Tool results provide component specifications for compatibility checks

### Handle infeasible or conflicting requirements gracefully
- **File**: `prompts.py`, `langgraph_agent.py`
- **Implementation**:
  - System prompt instructs to explain conflicts
  - Agent suggests alternatives when requirements are infeasible
  - Graceful degradation when tools fail

### Handle LLM API failures gracefully
- **File**: `langgraph_agent.py`
- **Implementation**:
  - 60-second timeout configuration
  - Error logging in `_log_step()`
  - Exception handling in graph execution
  - Fallback responses on failure

### Implement input validation and guard-rails
- **File**: `config.py`
- **Implementation**:
  - `Config.validate()` checks required configuration
  - Environment variable validation
  - Type conversion with error handling

### Add logging for each agent step
- **File**: `langgraph_agent.py`
- **Implementation**:
  - `_log_step()` method traces all agent actions
  - Logging to both file (`agent_trace.log`) and console
  - Timestamps and step types for debugging

## Task 4: Evaluation & Observability

### Define 3–5 representative test scenarios
- **File**: `evaluation.py`
- **Implementation**:
  - 5 test scenarios covering different use cases:
    1. Budget gaming PC ($1000)
    2. Content creation workstation ($2000)
    3. General office PC ($500)
    4. High-end gaming ($3000)
    5. Extreme budget constraints ($400)

### Provide lightweight evaluation
- **File**: `evaluation.py`
- **Implementation**:
  - `_evaluate_outcome()` checks for expected keywords
  - Qualitative evaluation against expected outcomes
  - Results saved to `test_results.json`

### Include trace/log of at least one full agent run
- **File**: `AGENT_RUN_REPORT.md`, `agent_trace.log`
- **Implementation**:
  - Full agent trace example in report
  - Detailed trace with timestamps and tool calls
  - Step-by-step reasoning chain documented

## Deliverables

### Source Code: Modular, readable Python project
- **Files**: All `.py` files
- **Implementation**:
  - Modular structure: separate files for agent, tools, data loader, config
  - Clean class-based design
  - Type hints and docstrings
  - Follows Python best practices

### Dependencies: requirements.txt
- **File**: `requirements.txt`
- **Implementation**: All dependencies listed with version constraints

### Configuration: .env.example with placeholders
- **File**: `.env.example`
- **Implementation**: Template with Ollama configuration placeholders

### README: Setup and run instructions, architecture overview, reproduction steps
- **File**: `README.md`
- **Implementation**:
  - Complete setup instructions
  - Architecture diagram
  - Running instructions for both CLI and web UI
  - Example interactions

### Agent Run Report: Architecture diagram, agent trace, design decisions
- **File**: `AGENT_RUN_REPORT.md`
- **Implementation**:
  - Architecture diagram
  - Full agent trace example
  - Detailed design decisions and trade-offs
  - Performance characteristics

## Bonus Features (Optional)

### Multi-agent orchestration
- **Status**: Not implemented (simplified to single agent for performance)

### Memory / conversation persistence across sessions
- **Status**: Partial - session persistence in Streamlit UI

### Streaming responses for real-time user interaction
- **File**: `app.py`, `langgraph_agent.py`
- **Implementation**:
  - Streamlit chat interface with real-time updates
  - LangChain-Ollama streaming integration
  - Response streaming in web UI

### Containerized deployment (Dockerfile or docker-compose)
- **Status**: Not implemented

### Simple UI (Streamlit, Gradio, or web frontend)
- **File**: `app.py`
- **Implementation**:
  - Complete Streamlit web UI
  - Chat-based interface
  - Agent trace viewer
  - Conversation history
