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
- Ollama installed and running

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

Edit `.env` and configure Ollama:
```
LLM_PROVIDER=ollama
MODEL_NAME=qwen2.5:7b
TEMPERATURE=0.7
MAX_RETRIES=3
```

**To set up Ollama:**
- Download and install Ollama from https://ollama.com
- Start the Ollama application
- Pull the required model: `ollama pull qwen2.5:7b`
- The agent will connect to Ollama automatically on http://127.0.0.1:11434

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

### Agent Architecture
- **LangGraph Framework**: Uses LangGraph for state-based agent orchestration with multiple nodes
- **Node-Based Workflow**: Separate nodes for requirement gathering, planning, tool execution, and reflection
- **State Management**: TypedDict-based state for tracking messages, requirements, and components
- **LangChain Integration**: Uses LangChain tools for component search and filtering
- **Conditional Edges**: Dynamic routing based on agent state and tool call results

### Prompt Engineering
- **Chain-of-Thought**: Structured reasoning template for better compatibility checking
- **Few-Shot Examples**: Included examples to guide requirement gathering and feedback handling
- **Self-Reflection**: Explicit reflection step to catch compatibility issues before finalizing

### Error Handling
- **Tenacity Retry**: Exponential backoff for LLM API failures
- **Graceful Degradation**: Tool failures return error messages instead of crashing
- **Input Validation**: Configuration validation on startup

### Trade-offs
- **Simplicity vs Features**: Prioritized working system over advanced features (streaming, UI, Docker)
- **Dataset Size**: Full dataset loaded into memory for fast queries; could be optimized for larger datasets
- **Compatibility Rules**: Basic compatibility checking; could be enhanced with a formal knowledge base

## Advanced Techniques Demonstrated

1. **LangGraph Orchestration**: State-based agent workflow with multiple nodes and conditional edges
2. **Chain-of-Thought Prompting**: Structured reasoning template for systematic component selection
3. **Self-Reflection**: Explicit validation step before final recommendations
4. **LangChain Tools**: Reliable tool execution with structured outputs
5. **Few-Shot Learning**: Examples in prompts to guide agent behavior
6. **Error Resilience**: Retry logic with exponential backoff

## Example Agent Trace

See `AGENT_RUN_REPORT.md` for a detailed agent run trace showing the full reasoning chain, tool calls, and decision-making process.

## License

MIT License
