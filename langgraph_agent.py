"""LangGraph-based PC Configuration Agent."""
import json
import logging
from typing import TypedDict, Annotated, List, Dict, Optional
from operator import add
from dataclasses import dataclass
from datetime import datetime

from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from tenacity import retry, stop_after_attempt, wait_exponential

from config import Config
from data_loader import ComponentDataLoader
from tools import ToolRegistry
import prompts

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_trace.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State for the LangGraph agent."""
    messages: Annotated[List, add]
    requirements: Optional[Dict]
    components: Dict[str, List[Dict]]
    current_step: str
    trace: List[Dict]


@dataclass
class AgentStep:
    """Represents a single step in the agent's reasoning chain."""
    timestamp: str
    step_type: str
    content: str
    tool_calls: Optional[List[Dict]] = None
    tool_results: Optional[List[str]] = None


class PCConfigAgentLangGraph:
    """PC Configuration Agent using LangGraph."""
    
    def __init__(self):
        Config.validate()
        
        # Initialize LLM using Groq with timeout
        self.llm = ChatGroq(
            model=Config.MODEL_NAME,
            temperature=Config.TEMPERATURE,
            api_key=Config.GROQ_API_KEY,
            timeout=60  # 60 second timeout for faster failure
        )
        
        # Initialize data loader and tools
        self.data_loader = ComponentDataLoader(Config.DATASET_PATH)
        self.tool_registry = ToolRegistry(self.data_loader)
        
        # Create LangChain tools
        self.langchain_tools = self._create_langchain_tools()
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.langchain_tools)
        
        # Build the graph
        self.graph = self._build_graph()
        
        self.trace: List[AgentStep] = []
        logger.info("LangGraph agent initialized successfully")
    
    def _create_langchain_tools(self):
        """Create LangChain tools from tool registry."""
        
        @tool
        def search_components(component_type: str, max_price: float = None, limit: int = 5) -> str:
            """Search for components by type with optional filters.
            
            Args:
                component_type: Type of component (cpu, motherboard, memory, etc.)
                max_price: Maximum price filter
                limit: Max results (default 5)
            """
            try:
                results = self.data_loader.search_components(
                    component_type=component_type,
                    filters=None,
                    max_price=max_price,
                    limit=limit
                )
                return json.dumps(results, indent=2, default=str)
            except Exception as e:
                return json.dumps({"error": str(e)})
        
        @tool
        def get_component_types() -> str:
            """List all available component types."""
            types = self.data_loader.get_component_types()
            return json.dumps(types, indent=2)
        
        @tool
        def get_component_schema(component_type: str) -> str:
            """Get available fields for a component type."""
            schema = self.data_loader.get_component_schema(component_type)
            return json.dumps(schema, indent=2)
        
        return [search_components, get_component_types, get_component_schema]
    
    def _log_step(self, step_type: str, content: str, tool_calls: Optional[List[Dict]] = None, tool_results: Optional[List[str]] = None):
        """Log a step in the agent's reasoning chain."""
        step = AgentStep(
            timestamp=datetime.now().isoformat(),
            step_type=step_type,
            content=content,
            tool_calls=tool_calls,
            tool_results=tool_results
        )
        self.trace.append(step)
        logger.info(f"Step: {step_type} - {content}")
    
    def _requirement_gatherer_node(self, state: AgentState) -> AgentState:
        """Node for gathering user requirements."""
        self._log_step("requirement_gathering", "Gathering requirements")
        
        system_prompt = f"{prompts.SYSTEM_PROMPT}\n\n{prompts.REQUIREMENT_GATHERING_PROMPT}\n\n{prompts.FEW_SHOT_EXAMPLES}"
        
        # Get last user message
        user_message = state["messages"][-1]
        
        messages = [
            ("system", system_prompt),
            user_message
        ]
        
        response = self.llm.invoke(messages)
        self._log_step("requirement_response", response.content)
        
        # Try to extract structured requirements
        extraction_messages = messages + [
            ("system", "Extract the requirements as JSON with fields: usage, budget, preferences, constraints. If information is missing, use null. Return ONLY the JSON, no other text."),
            ("assistant", response.content)
        ]
        
        extraction_response = self.llm.invoke(extraction_messages)
        
        try:
            requirements = json.loads(extraction_response.content)
            state["requirements"] = requirements
            self._log_step("requirements_extracted", json.dumps(requirements))
        except:
            state["requirements"] = None
        
        state["messages"].append(AIMessage(content=response.content))
        state["current_step"] = "requirements_gathered"
        
        return state
    
    def _planner_node(self, state: AgentState) -> AgentState:
        """Node for planning component selection."""
        self._log_step("planning", "Planning component selection strategy")
        
        system_prompt = f"{prompts.SYSTEM_PROMPT}\n\n{prompts.TOOL_USE_PROMPT}\n\n{prompts.CHAIN_OF_THOUGHT_TEMPLATE}"
        
        # Build conversation context
        conversation = system_prompt + "\n\n"
        for msg in state["messages"]:
            if isinstance(msg, HumanMessage):
                conversation += f"User: {msg.content}\n\n"
            elif isinstance(msg, AIMessage):
                conversation += f"Assistant: {msg.content}\n\n"
        
        if state["requirements"]:
            conversation += f"\nRequirements: {json.dumps(state['requirements'])}\n\n"
        
        response = self.llm.invoke([("system", conversation)])
        self._log_step("plan", response.content)
        
        state["messages"].append(AIMessage(content=response.content))
        state["current_step"] = "planned"
        
        return state
    
    def _tool_executor_node(self, state: AgentState) -> AgentState:
        """Node for executing tool calls."""
        self._log_step("tool_execution", "Executing tools")
        
        # Get last AI message
        last_message = state["messages"][-1]
        
        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            state["current_step"] = "no_tools"
            return state
        
        tool_calls = last_message.tool_calls
        self._log_step("tool_calls", f"Executing {len(tool_calls)} tool(s)", [tc for tc in tool_calls])
        
        tool_results = []
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # Find and execute the tool
            for lc_tool in self.langchain_tools:
                if lc_tool.name == tool_name:
                    try:
                        result = lc_tool.invoke(tool_args)
                        tool_results.append(result)
                        self._log_step("tool_result", f"{tool_name}: {str(result)[:200]}...")
                    except Exception as e:
                        error_msg = json.dumps({"error": str(e)})
                        tool_results.append(error_msg)
                        self._log_step("tool_error", f"{tool_name}: {str(e)}")
                    break
        
        # Add tool results to state
        for tool_call, result in zip(tool_calls, tool_results):
            state["messages"].append(ToolMessage(
                content=result,
                tool_call_id=tool_call["id"]
            ))
        
        state["current_step"] = "tools_executed"
        return state
    
    def _agent_node(self, state: AgentState) -> AgentState:
        """Main agent node that uses the LLM with tools."""
        self._log_step("agent_reasoning", "Agent reasoning with tools")
        
        # Get last message
        last_message = state["messages"][-1]
        
        # If last message was a tool result, we need to continue
        if isinstance(last_message, ToolMessage):
            # Invoke LLM with tool results
            response = self.llm_with_tools.invoke(state["messages"])
        else:
            # Initial invocation
            system_prompt = f"{prompts.SYSTEM_PROMPT}\n\n{prompts.TOOL_USE_PROMPT}\n\n{prompts.CHAIN_OF_THOUGHT_TEMPLATE}\n\n{prompts.REFLECTION_PROMPT}"
            
            # Build messages with system prompt
            messages = [("system", system_prompt)] + state["messages"]
            response = self.llm_with_tools.invoke(messages)
        
        self._log_step("agent_response", response.content)
        
        state["messages"].append(response)
        
        # Check if there are tool calls
        if hasattr(response, 'tool_calls') and response.tool_calls:
            state["current_step"] = "needs_tools"
        else:
            state["current_step"] = "complete"
        
        return state
    
    def _reflection_node(self, state: AgentState) -> AgentState:
        """Node for self-reflection and validation."""
        self._log_step("reflection", "Self-reflection and validation")
        
        system_prompt = f"{prompts.SYSTEM_PROMPT}\n\n{prompts.REFLECTION_PROMPT}"
        
        # Build conversation context
        conversation = system_prompt + "\n\n"
        for msg in state["messages"]:
            if isinstance(msg, HumanMessage):
                conversation += f"User: {msg.content}\n\n"
            elif isinstance(msg, AIMessage):
                conversation += f"Assistant: {msg.content}\n\n"
        
        response = self.llm.invoke([("system", conversation)])
        self._log_step("reflection_result", response.content)
        
        state["messages"].append(AIMessage(content=response.content))
        state["current_step"] = "reflected"
        
        return state
    
    def _should_continue_tools(self, state: AgentState) -> str:
        """Decide whether to continue using tools or finish."""
        if state["current_step"] == "needs_tools":
            return "tools"
        elif state["current_step"] == "tools_executed":
            return "agent"
        else:
            return "end"
    
    def _should_reflect(self, state: AgentState) -> str:
        """Decide whether to reflect or finish."""
        if state["current_step"] == "complete":
            return "reflect"
        else:
            return "end"
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("requirement_gatherer", self._requirement_gatherer_node)
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", self._tool_executor_node)
        workflow.add_node("reflection", self._reflection_node)
        
        # Set entry point
        workflow.set_entry_point("requirement_gatherer")
        
        # Add edges
        workflow.add_edge("requirement_gatherer", "planner")
        workflow.add_edge("planner", "agent")
        
        # Conditional edges for tool execution loop
        workflow.add_conditional_edges(
            "agent",
            self._should_continue_tools,
            {
                "tools": "tools",
                "end": "reflection"
            }
        )
        
        workflow.add_conditional_edges(
            "reflection",
            self._should_reflect,
            {
                "reflect": END,
                "end": END
            }
        )
        
        return workflow.compile()
    
    def invoke(self, user_input: str) -> Dict:
        """Invoke the agent with user input."""
        self.trace = []
        self._log_step("invocation_start", f"User input: {user_input}")
        
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "requirements": None,
            "components": {},
            "current_step": "start",
            "trace": []
        }
        
        try:
            final_state = self.graph.invoke(initial_state)
            
            # Get final response
            final_message = final_state["messages"][-1]
            final_response = final_message.content if hasattr(final_message, 'content') else str(final_message)
            
            self._log_step("invocation_complete", final_response)
            
            return {
                "response": final_response,
                "requirements": final_state.get("requirements"),
                "trace": self.trace,
                "messages": final_state["messages"]
            }
        except Exception as e:
            logger.error(f"Graph execution failed: {e}")
            self._log_step("error", str(e))
            return {
                "response": f"Error: {str(e)}",
                "requirements": None,
                "trace": self.trace,
                "messages": []
            }
    
    def handle_feedback(self, feedback: str, previous_state: Dict) -> Dict:
        """Handle user feedback with previous conversation context."""
        self._log_step("feedback_received", feedback)
        
        # Reconstruct state from previous context
        messages = previous_state.get("messages", [])
        messages.append(HumanMessage(content=feedback))
        
        initial_state = {
            "messages": messages,
            "requirements": previous_state.get("requirements"),
            "components": previous_state.get("components", {}),
            "current_step": "start",
            "trace": []
        }
        
        try:
            final_state = self.graph.invoke(initial_state)
            
            final_message = final_state["messages"][-1]
            final_response = final_message.content if hasattr(final_message, 'content') else str(final_message)
            
            self._log_step("feedback_handled", final_response)
            
            return {
                "response": final_response,
                "requirements": final_state.get("requirements"),
                "trace": self.trace,
                "messages": final_state["messages"]
            }
        except Exception as e:
            logger.error(f"Feedback handling failed: {e}")
            return {
                "response": f"Error: {str(e)}",
                "requirements": None,
                "trace": self.trace,
                "messages": []
            }
    
    def get_trace(self) -> List[AgentStep]:
        """Get the full reasoning trace."""
        return self.trace
    
    def reset(self):
        """Reset agent state."""
        self.trace = []
        logger.info("Agent state reset")
