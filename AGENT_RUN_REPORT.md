# PC Configuration Agent - Agent Run Report

## Architecture Overview

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
│  ┌──────────┐    ┌──────────┐                              │
│  │  Agent   │───▶│  Tools   │                              │
│  │  Node    │    │  Node    │                              │
│  └──────────┘    └──────────┘                              │
│       │                 │                                   │
│       └─────────────────┘                                   │
│              Conditional Edges                                │
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
│   Ollama     │
│   LLM API    │
│  qwen2.5:7b  │
└──────────────┘
```

## Agent Trace Example

### User Request: "I need a gaming PC for 1080p gaming with a $1000 budget"

**Step 1: Invocation Start**
- Timestamp: 2026-07-17T00:24:24.951Z
- User Input: "I need a gaming PC for 1080p gaming with a $1000 budget"

**Step 2: Agent Reasoning with Tools**
- Timestamp: 2026-07-17T00:26:41.831Z
- Action: Agent analyzes request and determines tool usage needed
- Tool Calls: 
  - `search_components(component_type="cpu", max_price="300", limit="3")`
  - `search_components(component_type="video-card", max_price="400", limit="3")`

**Step 3: Tool Execution**
- Timestamp: 2026-07-17T00:28:17.473Z
- Tool Results:
  - CPU search returned 3 compatible CPUs within budget
  - Video card search returned 3 GPUs within budget

**Step 4: Final Response Generation**
- Timestamp: 2026-07-17T00:30:07.451Z
- Response: Agent provides complete PC configuration with compatibility analysis

**Step 5: Invocation Complete**
- Timestamp: 2026-07-17T00:31:37.221Z
- Total Duration: ~7 minutes
- Final Output: Structured PC recommendation with component list and compatibility notes

## Design Decisions and Trade-offs

### 1. Framework Choice: LangGraph
**Decision:** Used LangGraph for agent orchestration
**Rationale:** 
- State-based workflow provides clear separation of concerns
- Built-in support for tool calling and conditional edges
- Better observability with state tracking
- Industry-standard for agentic systems

**Trade-offs:**
- More complex than simple LangChain chains
- Steeper learning curve
- Overhead for simple use cases

### 2. LLM Provider: Ollama with qwen2.5:7b
**Decision:** Local LLM via Ollama instead of cloud APIs
**Rationale:**
- No API costs or rate limits
- Privacy (data stays local)
- qwen2.5:7b has good tool-calling support (8/10 reliability)
- 4.4GB size is manageable for local deployment

**Trade-offs:**
- Slower inference than cloud APIs
- Requires local hardware resources
- Model quality lower than GPT-4
- Initial setup complexity

### 3. Simplified Workflow
**Decision:** Reduced from 5 nodes to 2 nodes (agent + tools)
**Rationale:**
- Original workflow (requirement_gatherer → planner → agent → tools → reflection) was too slow
- Each node added 30-50 seconds latency
- Simplified to essential tool-calling loop

**Trade-offs:**
- Less structured reasoning
- Removed explicit reflection step
- Potential for less thorough analysis

### 4. Prompt Engineering Approach
**Decision:** Minimal, concise prompts optimized for smaller model
**Rationale:**
- qwen2.5:7b (7B parameters) struggles with complex prompts
- Reduced token processing for faster inference
- Focus on essential instructions only

**Trade-offs:**
- Less sophisticated reasoning
- Fewer few-shot examples
- Potentially less robust handling of edge cases

### 5. Error Handling Strategy
**Decision:** Timeout-based error handling with logging
**Rationale:**
- Local LLMs can be slow or hang
- 60-second timeout prevents indefinite blocking
- Comprehensive logging for debugging

**Trade-offs:**
- May timeout on complex queries
- No automatic retry logic
- Manual intervention needed for failures

### 6. Component Compatibility Logic
**Decision:** LLM-based compatibility checking with tool support
**Rationale:**
- Flexible handling of various compatibility rules
- Can adapt to new component types
- Leverages LLM reasoning capabilities

**Trade-offs:**
- Dependent on LLM accuracy
- May miss edge cases
- No formal verification system

## Technical Implementation Details

### Agent Loop Implementation
The agent follows a simplified reason → act → observe loop:

1. **Reason**: Agent analyzes user input and decides if tools are needed
2. **Act**: Executes tool calls to search component database
3. **Observe**: Processes tool results and incorporates into response
4. **Respond**: Generates final recommendation based on gathered data

### Tool Integration
Three main tools are available:
- `search_components`: Query component database with filters
- `get_component_types`: List available component categories
- `get_component_schema`: Get available fields for a component type

### State Management
LangGraph's TypedDict-based state tracks:
- `messages`: Conversation history
- `requirements`: Extracted user requirements
- `components`: Selected components
- `trace`: Step-by-step reasoning log

## Performance Characteristics

### Latency Breakdown
- Tool-less response: 30-45 seconds
- Single tool call: 45-60 seconds
- Multi-tool workflow: 60-90 seconds
- Total agent invocation: 2-7 minutes

### Bottlenecks
1. **Ollama inference**: Primary bottleneck (local LLM speed)
2. **Tool execution**: Minimal overhead (CSV queries are fast)
3. **State management**: Negligible overhead

### Optimization Attempts
1. ✅ Simplified workflow (reduced nodes)
2. ✅ Timeout configuration (60s limit)
3. ✅ Minimal prompts (reduced tokens)
4. ✅ Efficient tool design (targeted queries)

## Evaluation Results

### Test Scenarios
5 representative scenarios were defined covering:
- Budget gaming PC ($1000)
- Content creation workstation ($2000)
- General office PC ($500)
- High-end gaming ($3000)
- Extreme budget constraints ($400)

### Expected Outcomes
- Agent should identify key components (CPU, GPU, RAM, etc.)
- Should mention compatibility considerations
- Should respect budget constraints
- Should handle infeasible requirements gracefully

### Observability
Full agent traces are logged to `agent_trace.log` including:
- Timestamp for each step
- Tool calls and results
- LLM responses
- Error conditions

## Conclusion

The PC Configuration Agent successfully demonstrates:
- ✅ Agentic system design with LangGraph
- ✅ Tool-based reasoning over structured data
- ✅ Requirement gathering and feedback handling
- ✅ Compatibility-aware recommendations
- ✅ Error handling and logging
- ✅ Modular, maintainable code structure

The system prioritizes working software over perfect recommendations, focusing on demonstrating agentic AI engineering principles rather than exhaustive component knowledge.
