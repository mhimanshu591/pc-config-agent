# PC Configuration Agent

An agentic AI system built with **LangGraph** that assists users in configuring compatible PC builds based on their requirements using a computer components dataset.

## Features

- **LangGraph Workflow**: State-based agent orchestration with multiple nodes
- **Requirement Gathering**: Collects user preferences for usage, budget, and constraints
- **Component Compatibility**: Ensures CPU socket, motherboard form factor, and other compatibility constraints
- **Tool-Based Reasoning**: Uses LangChain tools to search and filter components from dataset
- **Chain-of-Thought**: Structured reasoning with self-reflection for better recommendations
- **Feedback Loop**: Handles user feedback and adjusts recommendations accordingly
- **Error Handling**: Robust retry logic and graceful failure handling
- **Full Trace Logging**: Complete reasoning trace for debugging and analysis

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                         │
│                    (CLI / Interactive Mode)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   LangGraph Workflow                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  State Management (AgentState)                         │  │
│  │  - messages, requirements, components, trace           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │Requirement│───▶│ Planner  │───▶│  Agent   │              │
│  │ Gatherer │    │  Node    │    │  Node    │              │
│  └──────────┘    └──────────┘    └────┬─────┘              │
│                                      │                      │
│                              ┌───────▼──────┐              │
│                              │  Conditional  │              │
│                              │    Edges      │              │
│                              └───────┬──────┘              │
│                                      │                      │
│                    ┌─────────────────┼─────────────────┐    │
│                    ▼                 ▼                 ▼    │
│            ┌──────────┐      ┌──────────┐      ┌──────────┐│
│            │  Tools   │      │Reflection│      │   END    ││
│            │  Node    │◀─────│  Node    │      │          ││
│            └──────────┘      └──────────┘      └──────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   LangChain  │ │   Component  │ │   Config     │
│   Tools      │ │   Dataset    │ │  Management  │
│  - Search    │ │   (CSV)      │ │  (.env)      │
│  - Filter    │ │              │ │              │
│  - Schema    │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
         │
         ▼
┌──────────────┐
│   Gemini     │
│   LLM API    │
│              │
└──────────────┘
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Groq API key (free, ultra-fast inference) OR Gemini API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pc_config_agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` and configure your LLM provider:

**For Groq (recommended - ultra-fast):**
```
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=llama-3.3-70b-versatile
TEMPERATURE=0.7
MAX_RETRIES=3
```

**For Gemini:**
```
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-1.5-pro
TEMPERATURE=0.7
MAX_RETRIES=3
```

**To get a Groq API key:**
- Go to https://console.groq.com/keys
- Sign up for a free account (no credit card required)
- Copy your API key and add it to the `.env` file
- Groq provides 14,400 requests/day for free with ultra-fast inference

**To get a Gemini API key:**
- Go to https://makersuite.google.com/app/apikey
- Sign up for a Google account
- Create an API key and add it to the `.env` file

4. Ensure the dataset is available:
The agent expects the dataset at `../Computer_Components_Dataset/data/csv` relative to the project root. Update the `DATASET_PATH` in `.env` if your dataset is located elsewhere.

## Running the Agent

### Interactive Mode (CLI)

```bash
python main.py
```

### Web UI (Streamlit)

For a better user experience, run the Streamlit web interface:

```bash
streamlit run app.py
```

The web UI provides:
- Chat-based interface
- Real-time agent responses
- Conversation history
- Agent trace viewer
- Clear conversation button

Example interaction:
```
=== PC Configuration Agent ===

Agent ready. Type 'quit' to exit.

You: I need a gaming PC for 1080p gaming with a $1000 budget

Agent: Gathering requirements...
[Agent responds with clarifying questions and then provides recommendation]

You: Can you make the CPU cheaper?

Agent: Processing your feedback...
[Agent adjusts recommendation]
```

### Running Evaluation Tests

```bash
python evaluation.py
```

This runs 5 test scenarios and saves results to `test_results.json`.

## Project Structure

```
pc_config_agent/
├── langgraph_agent.py    # LangGraph-based agent implementation
├── config.py             # Configuration management
├── data_loader.py        # Dataset loading and component search
├── tools.py              # Tool definitions and registry
├── prompts.py            # System prompts and templates
├── main.py               # CLI entry point
├── evaluation.py         # Test scenarios and evaluation
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable template
├── README.md             # This file
└── agent_trace.log       # Runtime trace logs (generated)
```

## Component Types Supported

- CPU
- Motherboard
- Memory (RAM)
- Video Card (GPU)
- Power Supply
- Case
- Internal Hard Drive (Storage)
- CPU Cooler

## Design Decisions

### Agent Architecture (Current)
- **LangGraph Framework**: Uses LangGraph for state-based agent orchestration
- **Node-Based Workflow**: 3 nodes (agent → tools → final_response) for single-pass execution
- **State Management**: TypedDict-based state for tracking messages, requirements, and components
- **LangChain Integration**: Uses LangChain tools with Pydantic schemas for component search
- **Conditional Edges**: Dynamic routing based on agent state and tool call results
- **LLM Support**: Groq (llama-3.3-70b-versatile) or Gemini (gemini-1.5-pro)

### Prompt Engineering
- **Chain-of-Thought**: Step-by-step reasoning instructions for systematic component selection
- **Compatibility Rules**: Explicit compatibility constraints in system prompt
- **Tool Instructions**: Clear guidance on when and how to use search_components tool

### Error Handling
- **Tenacity Retry**: Exponential backoff for LLM API failures
- **Graceful Degradation**: Tool failures return error messages instead of crashing
- **Input Validation**: Configuration validation on startup

### Trade-offs
- **Single-Pass Workflow**: Prioritized speed and reliability over multi-step reasoning
- **Simplified Tools**: Removed schema/type tools to prevent infinite loops
- **Cloud vs Local**: Chose cloud API for speed over local privacy
- **Component Coverage**: Some component types may have empty results in dataset
- **LLM Flexibility**: Supports both Groq (fast) and Gemini (robust)

## Advanced Techniques Demonstrated

1. **LangGraph Orchestration**: State-based agent workflow with simplified single-pass execution
2. **Chain-of-Thought Prompting**: Step-by-step reasoning instructions for systematic component selection
3. **Pydantic Schemas**: Structured tool parameter validation for reliable tool calling
4. **LangChain Tools**: Reliable tool execution with structured outputs
5. **Groq Integration**: Ultra-fast cloud LLM with excellent tool-calling support
6. **Error Resilience**: Retry logic with exponential backoff via tenacity
7. **Colored Debugging**: Real-time visual feedback for agent workflow steps

## Example Agent Trace

See `AGENT_RUN_REPORT.md` for a detailed agent run trace showing the full reasoning chain, tool calls, and decision-making process.

## License

MIT License
