import os
import json
import re
import asyncio
import logging
import uuid
from typing import TypedDict, Annotated, List, Union, Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from sqlalchemy.orm import Session
from .tools import ShoppingTools
import operator
from dotenv import load_dotenv

load_dotenv()

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TechShopAgent")

# Context Adapter for Request ID logging
class RequestAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        req_id = self.extra.get('request_id', 'unknown')
        return '[Req: %s] %s' % (req_id, msg), kwargs

# --- Guardrails Configuration ---
MAX_TOOL_STEPS = 5
MAX_TOOL_INPUT_CHAR = 500
TOOL_TIMEOUT_SECONDS = 10

class SecurityGuard:
    # Basic patterns for demonstration
    PII_PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
        "credit_card": r'\b(?:\d[ -]*?){13,16}\b'
    }

    @classmethod
    def sanitize(cls, text: str) -> str:
        if not text:
            return text
        
        cleaned = text
        # Redact PII
        for ptype, pattern in cls.PII_PATTERNS.items():
            cleaned = re.sub(pattern, f"[REDACTED_{ptype.upper()}]", cleaned)
             
        return cleaned

    @classmethod
    def validate_tool_input(cls, tool_name: str, tool_args: dict) -> tuple[bool, str]:
        # Check size limits
        args_str = json.dumps(tool_args)
        if len(args_str) > MAX_TOOL_INPUT_CHAR:
             return False, f"Input too large for tool {tool_name} (max {MAX_TOOL_INPUT_CHAR} chars)"
        return True, ""

def get_model():
    try:
        # Using a model with good tool calling capabilities is important.
        model_name = os.getenv("OPENAI_MODEL", "gpt-5-mini")
        return ChatOpenAI(temperature=0, model=model_name, streaming=True)
    except Exception:
        return None

# Define the state
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    # Track steps to prevent infinite loops
    step_count: Annotated[int, operator.add]
    # Request ID for tracing
    request_id: str

# We need to create the graph dynamically per request to inject the db session
def create_agent_graph(db: Session, session_id: str):
    shopping_tools = ShoppingTools(db, session_id)

    # --- Tool Definitions ---

    @tool
    def search_products(query: str, min_price: float = None, max_price: float = None, brand: str = None, category: Literal["phone", "laptop", "accessory"] = None):
        """
        Search for products by name, brand, or category. 
        Supports optional filtering by price range (min_price, max_price), brand, and category.
        Valid categories: 'phone', 'laptop', 'accessory'.
        Use this to find products when the user asks for recommendations, specific items, or filters by price/brand.
        Returns a list of products with 'display_id' and 'product_id'.
        """
        results = shopping_tools.search_products(query, min_price, max_price, brand, category)
        return json.dumps(results)

    @tool
    def get_cart():
        """
        Retrieve the latest shopping cart items, quantities, and total price from the database.
        Also triggers a navigation to the cart page.
        MUST be called to get accurate cart information as the user may modify it externally.
        Returns a JSON object with 'items', 'total', and 'action'.
        """
        return json.dumps(shopping_tools.get_cart_summary())

    @tool
    def add_to_cart(product_id: str, quantity: int = 1):
        """
        Add a product to the cart. 
        Accepts 'product_id' which can be:
        1. The 5-digit display_id shown to the user.
        2. The UUID string.
        3. The product name (e.g. "iPhone 16").
        Returns a JSON string with action details.
        """
        result = shopping_tools.add_to_cart(product_id, quantity)
        return json.dumps(result)

    @tool
    def remove_from_cart(product_id: str):
        """
        Remove a product from the cart.
        Accepts 'product_id' which can be UUID, 5-digit display_id, or product name.
        """
        result = shopping_tools.remove_from_cart(product_id)
        return json.dumps(result)

    @tool
    def update_cart_quantity(product_id: str, quantity: int):
        """
        Update the quantity of a product in the cart.
        Accepts 'product_id' (UUID, 5-digit display_id, or name) and the new 'quantity'.
        """
        result = shopping_tools.update_cart_quantity(product_id, quantity)
        return json.dumps(result)

    @tool
    def get_product_details(product_ids: List[str]):
        """
        Get detailed specs for one or more products.
        Useful for comparing products.
        Accepts a list of 'product_id's (UUIDs or 5-digit display_ids).
        """
        products = shopping_tools.validate_products(product_ids)
        return json.dumps(products)

    @tool
    def navigate_to_product(product_id: str):
        """
        Navigate the user to a specific product page.
        Use this when the user explicitly asks to view or go to a product.
        Accepts 'product_id' (UUID or 5-digit display_id).
        Returns a structured navigation action.
        """
        # We verify the product exists first
        product = shopping_tools.get_product_by_id(product_id)
        if not product:
            return json.dumps({"error": "Product not found."})
            
        return json.dumps({
            "action": "navigate",
            "product_id": product['product_id'], # Return the real UUID for the frontend
            "target": f"/shop/{product['product_id']}"
        })

    tools = [
        search_products, 
        get_cart, 
        add_to_cart, 
        remove_from_cart, 
        update_cart_quantity,
        get_product_details,
        navigate_to_product
    ]

    model = get_model()
    if not model:
        # Fallback if no API key
        return None

    model_with_tools = model.bind_tools(tools)

    # --- Node Definitions ---

    # Input Guard Node
    def input_guard(state: AgentState):
        messages = state['messages']
        last_msg = messages[-1]
        req_id = state.get('request_id', 'unknown')
        adapter = RequestAdapter(logger, {'request_id': req_id})
        
        if isinstance(last_msg, HumanMessage):
             # Sanitize user input
             clean_content = SecurityGuard.sanitize(last_msg.content)
             adapter.info(f"User Input Received: {clean_content}") # Log sanitized input
             if clean_content != last_msg.content:
                 adapter.warning(f"Sanitization triggered on input.")
                 # Replace the message content with sanitized version
                 last_msg.content = clean_content
        return {"step_count": 0} # Reset or init step count

    async def chatbot(state: AgentState, config: RunnableConfig):
        messages = state['messages']
        req_id = state.get('request_id', 'unknown')
        adapter = RequestAdapter(logger, {'request_id': req_id})
        
        # Model Retry Logic
        max_retries = 2
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                response = await model_with_tools.ainvoke(messages, config)
                
                # Output Guard: Sanitize AI response
                if isinstance(response.content, str):
                    original_len = len(response.content)
                    response.content = SecurityGuard.sanitize(response.content)
                    if len(response.content) != original_len:
                         adapter.warning("Sanitization triggered on AI output.")

                adapter.info(f"Model Response: {response.content[:200]}..." if response.content else "Model Response: [Tool Call]")
                    
                return {"messages": [response], "step_count": 1} # Increment step
            except Exception as e:
                adapter.error(f"Model invocation failed (Attempt {attempt+1}/{max_retries}): {e}")
                last_exception = e
                # If it's a context window error or similar, maybe don't retry. 
                # For now we retry everything.
                continue
        
        # Fallback if model fails after retries
        adapter.critical(f"Model failed all retries. Last error: {last_exception}")
        fallback_prompts = get_fallback_prompts()
        error_msg = fallback_prompts.get("model_error", "I apologize, but I'm having trouble thinking right now. Please try asking again later.")
        return {
            "messages": [AIMessage(content=error_msg)],
            "step_count": 1
        }

    async def tool_node(state: AgentState, config: RunnableConfig):
        messages = state['messages']
        last_message = messages[-1]
        req_id = state.get('request_id', 'unknown')
        adapter = RequestAdapter(logger, {'request_id': req_id})
        
        tool_outputs = []
        
        # Determine which tool to call
        if hasattr(last_message, "tool_calls"):
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]
                
                adapter.info(f"Tool Call: {tool_name} | Args: {SecurityGuard.sanitize(json.dumps(tool_args))}")

                # Validation Guard
                is_valid, error_msg = SecurityGuard.validate_tool_input(tool_name, tool_args)
                if not is_valid:
                    adapter.error(f"Tool Validation Failed: {error_msg}")
                    tool_outputs.append(ToolMessage(content=f"Error: {error_msg}", tool_call_id=tool_id))
                    continue

                # Find the tool function
                selected_tool = next((t for t in tools if t.name == tool_name), None)
                
                if selected_tool:
                    try:
                        # Invoke the tool with config to propagate events
                        # We use ainvoke and asyncio.wait_for for timeout protection
                        task = selected_tool.ainvoke(tool_args, config=config)
                        output = await asyncio.wait_for(task, timeout=TOOL_TIMEOUT_SECONDS)
                        adapter.info(f"Tool Success: {tool_name}")
                    except asyncio.TimeoutError:
                        adapter.error(f"Tool Timeout: {tool_name}")
                        output = f"Error: Tool {tool_name} timed out after {TOOL_TIMEOUT_SECONDS} seconds."
                    except Exception as e:
                        adapter.error(f"Tool Execution Failed: {tool_name} | Error: {e}")
                        # Failure Policy: Graceful error return
                        output = f"Error executing tool {tool_name}: {str(e)}. Please try again with valid arguments."
                else:
                    adapter.error(f"Tool Not Found: {tool_name}")
                    output = f"Error: Tool {tool_name} not found."
                    
                tool_outputs.append(ToolMessage(content=str(output), tool_call_id=tool_id))
                
        return {"messages": tool_outputs}

    def fallback(state: AgentState):
        """Fallback node for when the agent gets stuck or exceeds limits."""
        req_id = state.get('request_id', 'unknown')
        adapter = RequestAdapter(logger, {'request_id': req_id})
        adapter.warning("Fallback Triggered: Loop limit exceeded.")
        
        return {
            "messages": [AIMessage(content="I apologize, but I seem to be going in circles or taking too long. Could you please rephrase your request?")]
        }

    def should_continue(state: AgentState) -> Literal["tools", "fallback", "__end__"]:
        messages = state['messages']
        last_message = messages[-1]
        step_count = state.get("step_count", 0)
        
        # Loop Guard
        if step_count > MAX_TOOL_STEPS:
            return "fallback"
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "__end__"

    # --- Graph Construction ---
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node("input_guard", input_guard)
    workflow.add_node("chatbot", chatbot)
    workflow.add_node("tools", tool_node)
    workflow.add_node("fallback", fallback)
    
    workflow.set_entry_point("input_guard")
    
    workflow.add_edge("input_guard", "chatbot")
    
    workflow.add_conditional_edges(
        "chatbot",
        should_continue,
        {
            "continue": "tools",
            "max_tool_steps": "fallback",
            "end": END,
        },
    )
    
    workflow.add_edge("tools", "chatbot")
    workflow.add_edge("fallback", END)
    
    return workflow.compile()

async def run_agent(messages: List[Dict[str, str]], db: Session, session_id: str, request_id: str = None):
    """
    Run the agent with the given messages and database session.
    """
    if not request_id:
        request_id = str(uuid.uuid4())
        
    app = create_agent_graph(db, session_id)
    
    if not app:
        return "I'm currently offline (OpenAI API Unavailable)."

    # Convert inputs to LangChain format
    langchain_messages = []
    for msg in messages:
        if msg["role"] == "user":
            content = SecurityGuard.sanitize(msg["content"]) # Sanitize input immediately
            langchain_messages.append(HumanMessage(content=content))
        elif msg["role"] == "assistant":
            langchain_messages.append(AIMessage(content=msg["content"]))
        elif msg["role"] == "system":
            langchain_messages.append(SystemMessage(content=msg["content"]))
            
    inputs = {"messages": langchain_messages, "step_count": 0, "request_id": request_id}
    
    # Run the graph
    config = {
        "run_name": "TechShopAgent",
        "metadata": {
            "request_id": request_id,
            "session_id": session_id,
        },
    }
    final_state = await app.ainvoke(inputs, config=config)
    
    # Return the content of the last message
    return final_state["messages"][-1].content

async def run_agent_stream(messages: List[Dict[str, str]], db: Session, session_id: str, request_id: str = None):
    """
    Stream the agent's response token by token.
    """
    if not request_id:
        request_id = str(uuid.uuid4())

    app = create_agent_graph(db, session_id)
    
    if not app:
        yield "I'm currently offline (OpenAI API Unavailable)."
        return

    # Convert inputs to LangChain format
    langchain_messages = []
    for msg in messages:
        if msg["role"] == "user":
            content = SecurityGuard.sanitize(msg["content"]) # Sanitize input
            langchain_messages.append(HumanMessage(content=content))
        elif msg["role"] == "assistant":
            langchain_messages.append(AIMessage(content=msg["content"]))
        elif msg["role"] == "system":
            langchain_messages.append(SystemMessage(content=msg["content"]))
            
    inputs = {"messages": langchain_messages, "step_count": 0, "request_id": request_id}
    
    # Track if we have streamed any content to handle fallback cases
    has_streamed = False
    
    # Stream events
    config = {
        "run_name": "TechShopAgent",
        "metadata": {
            "request_id": request_id,
            "session_id": session_id,
        },
    }
    async for event in app.astream_events(inputs, version="v1", config=config):
        kind = event["event"]
        
        if kind == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            if hasattr(chunk, "content") and chunk.content:
                has_streamed = True
                yield chunk.content
                
        elif kind == "on_tool_end":
            tool_name = event["name"]
            if tool_name in ["add_to_cart", "navigate_to_product", "remove_from_cart", "update_cart_quantity", "get_cart"]:
                output = event["data"].get("output")
                if output and isinstance(output, str):
                    yield f"\n```json\n{output}\n```\n"
                    
        elif kind == "on_chain_end":
            # Check for fallback or static responses that weren't streamed
            node_name = event.get("name")
            if node_name in ["chatbot", "fallback"] and not has_streamed:
                # Try to get the output message content
                output = event.get("data", {}).get("output")
                if output and isinstance(output, dict) and "messages" in output:
                    msgs = output["messages"]
                    if msgs and isinstance(msgs, list):
                        last_msg = msgs[-1]
                        if isinstance(last_msg, (AIMessage, BaseMessage)) and last_msg.content:
                            yield last_msg.content
                            has_streamed = True
