import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from backend.app.agent import create_agent_graph, SecurityGuard, MAX_TOOL_STEPS

# Mock the database session
@pytest.fixture
def mock_db():
    return MagicMock()

# Mock ShoppingTools
@pytest.fixture
def mock_shopping_tools():
    with patch("backend.app.agent.ShoppingTools") as MockTools:
        tools_instance = MockTools.return_value
        # Default behaviors
        tools_instance.search_products.return_value = [{"product_id": "123", "name": "Test Product"}]
        yield tools_instance

# Mock ChatOpenAI
@pytest.fixture
def mock_llm():
    with patch("backend.app.agent.ChatOpenAI") as MockClass:
        mock_instance = MockClass.return_value
        # Mock bind_tools to return self (since we just chain it)
        mock_instance.bind_tools.return_value = mock_instance
        # Default response
        mock_instance.ainvoke = AsyncMock(return_value=AIMessage(content="I can help with that."))
        yield mock_instance

@pytest.mark.asyncio
async def test_security_guard_sanitization():
    """Test PII redaction and bad word filtering."""
    # Email
    text = "Contact me at test@example.com"
    sanitized = SecurityGuard.sanitize(text)
    assert "[REDACTED_EMAIL]" in sanitized
    assert "test@example.com" not in sanitized

    # Phone
    text = "Call 123-456-7890"
    sanitized = SecurityGuard.sanitize(text)
    assert "[REDACTED_PHONE]" in sanitized

@pytest.mark.asyncio
async def test_tool_input_validation():
    """Test tool input validation logic."""
    # Valid input
    valid, msg = SecurityGuard.validate_tool_input("search_products", {"query": "iphone"})
    assert valid is True
    
    # Invalid input (too large)
    large_input = {"query": "a" * 1000}
    valid, msg = SecurityGuard.validate_tool_input("search_products", large_input)
    assert valid is False
    assert "Input too large" in msg

@pytest.mark.asyncio
async def test_agent_workflow_basic_chat(mock_db, mock_shopping_tools, mock_llm):
    """Test a simple user-agent turn without tools."""
    # Mock LLM to return a simple string
    mock_llm.ainvoke.return_value = AIMessage(content="Hello! How can I help you?")

    app = create_agent_graph(mock_db, "session_123")
    
    inputs = {
        "messages": [HumanMessage(content="Hello")],
        "step_count": 0,
        "request_id": "req_123"
    }
    
    result = await app.ainvoke(inputs)
    
    messages = result["messages"]
    # Check that we got a response
    assert len(messages) >= 2
    assert messages[-1].content == "Hello! How can I help you?"
    # Verify step count incremented
    assert result.get("step_count", 0) == 1

@pytest.mark.asyncio
async def test_agent_loop_guard(mock_db, mock_shopping_tools, mock_llm):
    """Test that the agent falls back when step count exceeds limit."""
    app = create_agent_graph(mock_db, "session_123")
    
    # Start with step_count > limit
    # MAX_TOOL_STEPS is 5. If we come in with 6, 'chatbot' node runs -> increments to 7.
    # Then 'should_continue' sees 7 > 5 -> returns "fallback".
    inputs = {
        "messages": [HumanMessage(content="Loop me")],
        "step_count": MAX_TOOL_STEPS + 1,
        "request_id": "req_123"
    }
    
    mock_llm.ainvoke.return_value = AIMessage(content="Still trying...")
    
    result = await app.ainvoke(inputs)
    
    messages = result["messages"]
    last_msg = messages[-1]
    
    # Verify we hit the fallback message
    assert "apologize" in last_msg.content.lower()
    assert "circles" in last_msg.content.lower()

@pytest.mark.asyncio
async def test_agent_tool_execution_flow(mock_db, mock_shopping_tools, mock_llm):
    """Test that tool calls are routed correctly."""
    app = create_agent_graph(mock_db, "session_123")
    
    # 1. User says "find iphone"
    # 2. LLM responds with tool call
    # 3. Agent executes tool
    # 4. Agent goes back to LLM (we'll just check it hits the tool node)

    # Setup LLM to return a tool call first
    tool_call_msg = AIMessage(
        content="",
        tool_calls=[{
            "name": "search_products",
            "args": {"query": "iphone"},
            "id": "call_123"
        }]
    )
    
    # We mock the LLM to return the tool call
    mock_llm.ainvoke.return_value = tool_call_msg
    
    # We need to run the graph. 
    # Since the graph loop will continue until __end__, we need to change the mock 
    # for the SECOND call to return a final answer, otherwise it might loop if the logic decides to call tool again.
    # However, in 'chatbot' node, we call model.ainvoke.
    # We can use side_effect to return different values on subsequent calls.
    
    final_response = AIMessage(content="Here are the iphones I found.")
    mock_llm.ainvoke.side_effect = [tool_call_msg, final_response]

    inputs = {
        "messages": [HumanMessage(content="find iphone")],
        "step_count": 0,
        "request_id": "req_123"
    }
    
    result = await app.ainvoke(inputs)
    
    messages = result["messages"]
    
    # Verify sequence: Human -> AI (Tool Call) -> ToolMessage -> AI (Final)
    # Note: StateGraph accumulates messages.
    
    # Let's check if search_products was called on our mock tools
    mock_shopping_tools.search_products.assert_called_with("iphone", None, None, None, None)
    
    # Check messages
    assert len(messages) >= 4
    assert isinstance(messages[-3], AIMessage) # Tool Call
    assert isinstance(messages[-2], ToolMessage) # Tool Output
    assert isinstance(messages[-1], AIMessage) # Final Response
    assert messages[-1].content == "Here are the iphones I found."

@pytest.mark.asyncio
async def test_agent_tool_execution_with_filters(mock_db, mock_shopping_tools, mock_llm):
    """Test that tool calls with filters are routed correctly."""
    app = create_agent_graph(mock_db, "session_123")
    
    # LLM returns tool call with filters
    tool_call_msg = AIMessage(
        content="",
        tool_calls=[{
            "name": "search_products",
            "args": {"query": "iphone", "max_price": 1000.0, "brand": "Apple"},
            "id": "call_124"
        }]
    )
    
    # We need a sequence for the loop
    final_response = AIMessage(content="Here are the filtered iphones.")
    mock_llm.ainvoke.side_effect = [tool_call_msg, final_response]

    inputs = {
        "messages": [HumanMessage(content="find cheap apple iphone")],
        "step_count": 0,
        "request_id": "req_124"
    }
    
    await app.ainvoke(inputs)
    
    # Check call args
    mock_shopping_tools.search_products.assert_called_with("iphone", None, 1000.0, "Apple", None)

@pytest.mark.asyncio
async def test_agent_get_cart_navigation(mock_db, mock_shopping_tools, mock_llm):
    """Test that asking for cart triggers navigation action."""
    app = create_agent_graph(mock_db, "session_123")
    
    # Configure mock to return the navigation dict with items
    mock_shopping_tools.get_cart_summary.return_value = {
        "items": [
            {
                "product_id": "123",
                "name": "IPhone 16",
                "quantity": 1,
                "price": 999.00,
                "total": 999.00
            }
        ],
        "total": 999.00,
        "item_count": 1,
        "action": "navigate",
        "target": "/cart",
        "message": "Here is your cart."
    }
    
    # LLM tool call
    tool_call_msg = AIMessage(
        content="",
        tool_calls=[{
            "name": "get_cart",
            "args": {},
            "id": "call_cart"
        }]
    )
    
    final_response = AIMessage(content="Opening your cart.")
    mock_llm.ainvoke.side_effect = [tool_call_msg, final_response]
    
    inputs = {
        "messages": [HumanMessage(content="show my cart")],
        "step_count": 0,
        "request_id": "req_cart"
    }
    
    result = await app.ainvoke(inputs)
    
    # Verify tool was called
    mock_shopping_tools.get_cart_summary.assert_called_once()
    
    messages = result["messages"]
    # Verify the output message contains the JSON from the tool
    # The tool output is wrapped in ToolMessage
    tool_msg = messages[-2]
    assert isinstance(tool_msg, ToolMessage)
    
    # The tool output should be JSON string
    content = tool_msg.content
    try:
        data = json.loads(content)
        assert data["action"] == "navigate"
        assert data["target"] == "/cart"
        assert "items" in data
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "IPhone 16"
        assert data["total"] == 999.00
    except json.JSONDecodeError:
        pytest.fail(f"Tool output is not valid JSON: {content}")
