import os
import uuid
from typing import List

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from backend.app.database import Base
from backend.app.models import Product, Cart, CartItem, SearchResult
from backend.app.utils.prompts import get_system_prompt


def _should_run_real_llm_eval() -> bool:
    return (
        os.getenv("RUN_REAL_LLM_EVAL") == "1"
        and bool(os.getenv("OPENAI_API_KEY"))
        and bool(os.getenv("DATABASE_URL"))
    )


REAL_LLM_SKIP_REASON = (
    "Real-LLM evals are disabled. Set RUN_REAL_LLM_EVAL=1, OPENAI_API_KEY, and DATABASE_URL."
)


def _ensure_real_llm_prereqs_or_skip():
    if not _should_run_real_llm_eval():
        pytest.skip(REAL_LLM_SKIP_REASON)

    try:
        import langgraph  # noqa: F401
    except ModuleNotFoundError:
        pytest.skip("Missing dependency: langgraph. Install backend requirements before running evals.")


def _extract_tool_names(messages: List[object]) -> List[str]:
    names: List[str] = []
    for m in messages:
        if isinstance(m, AIMessage) and getattr(m, "tool_calls", None):
            for tc in m.tool_calls:
                n = tc.get("name")
                if n:
                    names.append(n)
    return names


def _extract_tool_calls(messages: List[object]) -> List[dict]:
    tool_calls: List[dict] = []
    for m in messages:
        if isinstance(m, AIMessage) and getattr(m, "tool_calls", None):
            for tc in m.tool_calls:
                tool_calls.append(tc)
    return tool_calls


def _ensure_seed_products(db):
    """Ensure at least a couple known products exist. Keep it minimal and deterministic."""

    def ensure_one(
        *,
        product_id: str,
        name: str,
        brand: str,
        category: str,
        price_cents: int,
    ):
        existing = db.query(Product).filter(Product.product_id == product_id).first()
        if existing:
            return
        db.add(
            Product(
                product_id=product_id,
                name=name,
                brand=brand,
                category=category,
                price_cents=price_cents,
                currency="USD",
                aliases=[],
                specs={},
                rating=4.5,
                popularity=100,
                image_url="",
                is_active=True,
            )
        )

    ensure_one(
        product_id="PHN-APL-IPH15P",
        name="iPhone 15 Pro",
        brand="Apple",
        category="phone",
        price_cents=99900,
    )
    ensure_one(
        product_id="ACC-LOG-MX3S",
        name="Logitech MX Master 3S",
        brand="Logitech",
        category="accessory",
        price_cents=9900,
    )

    db.commit()


def _clear_session_state(db, session_id: str):
    # Search mappings
    db.query(SearchResult).filter(SearchResult.session_id == session_id).delete()

    # Cart + items
    cart = db.query(Cart).filter(Cart.session_id == session_id).first()
    if cart:
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        db.query(Cart).filter(Cart.id == cart.id).delete()

    db.commit()


@pytest.mark.asyncio
@pytest.mark.skipif(not _should_run_real_llm_eval(), reason=REAL_LLM_SKIP_REASON)
async def test_real_llm_tool_accuracy_cart_flow():
    """End-to-end tool accuracy (real LLM): search -> add -> update qty -> remove -> get cart."""

    _ensure_real_llm_prereqs_or_skip()

    # Import after env + dependency checks so collection never errors.
    from backend.app.agent import create_agent_graph

    db_url = os.environ["DATABASE_URL"]
    engine = create_engine(db_url)

    # Ensure tables exist (Postgres expected)
    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    session_id = f"eval_{uuid.uuid4().hex}"

    db = Session()
    try:
        _ensure_seed_products(db)
        _clear_session_state(db, session_id)

        graph = create_agent_graph(db, session_id)
        assert graph is not None, "Agent graph could not be created (check OPENAI_API_KEY / model)."

        sys_prompt = get_system_prompt() or {}
        sys_msg = SystemMessage(content=sys_prompt.get("content", ""))

        # ---- Turn 1: search ----
        messages = [
            sys_msg,
            HumanMessage(
                content=(
                    "Call the tool `search_products` with these exact args: "
                    "query='iphone', category='phone', brand='Apple', max_price=1200. "
                    "Do not ask clarifying questions. After calling the tool, reply briefly."
                )
            ),
        ]

        out1 = await graph.ainvoke({"messages": messages, "step_count": 0, "request_id": "eval_req_1"})
        tool_calls_1 = _extract_tool_calls(out1["messages"])
        search_calls = [tc for tc in tool_calls_1 if tc.get("name") == "search_products"]
        assert search_calls, "Expected the model to call search_products"
        search_args = search_calls[0].get("args") or {}
        assert str(search_args.get("category")) == "phone"
        assert str(search_args.get("brand")).lower() == "apple"
        assert "iphone" in str(search_args.get("query", "")).lower()
        assert float(search_args.get("max_price")) >= 1100

        mapping = (
            db.query(SearchResult)
            .filter(SearchResult.session_id == session_id)
            .order_by(SearchResult.created_at.desc())
            .first()
        )
        assert mapping is not None, "Expected at least one SearchResult mapping for this session."
        display_id = str(mapping.display_id)
        mapped_product_id = mapping.product_id

        # ---- Turn 2: add to cart via display_id ----
        out2 = await graph.ainvoke(
            {
                "messages": [
                    sys_msg,
                    HumanMessage(
                        content=(
                            f"Call the tool `add_to_cart` with args: product_id='{display_id}', quantity=1. "
                            "Do not call any other tools. Reply briefly after tool execution."
                        )
                    ),
                ],
                "step_count": 0,
                "request_id": "eval_req_2",
            }
        )
        tool_calls_2 = _extract_tool_calls(out2["messages"])
        add_calls = [tc for tc in tool_calls_2 if tc.get("name") == "add_to_cart"]
        assert add_calls, "Expected the model to call add_to_cart"
        add_args = add_calls[0].get("args") or {}
        assert str(add_args.get("product_id")) == display_id

        cart = db.query(Cart).filter(Cart.session_id == session_id).first()
        assert cart is not None

        item = (
            db.query(CartItem)
            .filter(CartItem.cart_id == cart.id, CartItem.product_id == mapped_product_id)
            .first()
        )
        assert item is not None
        assert item.quantity >= 1

        # ---- Turn 3: update quantity ----
        out3 = await graph.ainvoke(
            {
                "messages": [
                    sys_msg,
                    HumanMessage(
                        content=(
                            f"Call the tool `update_cart_quantity` with args: product_id='{display_id}', quantity=2. "
                            "Do not call any other tools. Reply briefly."
                        )
                    ),
                ],
                "step_count": 0,
                "request_id": "eval_req_3",
            }
        )
        tool_calls_3 = _extract_tool_calls(out3["messages"])
        upd_calls = [tc for tc in tool_calls_3 if tc.get("name") == "update_cart_quantity"]
        assert upd_calls, "Expected the model to call update_cart_quantity"
        upd_args = upd_calls[0].get("args") or {}
        assert str(upd_args.get("product_id")) == display_id
        assert int(upd_args.get("quantity")) == 2

        db.refresh(item)
        item = (
            db.query(CartItem)
            .filter(CartItem.cart_id == cart.id, CartItem.product_id == mapped_product_id)
            .first()
        )
        assert item is not None
        assert item.quantity == 2

        # ---- Turn 4: remove ----
        out4 = await graph.ainvoke(
            {
                "messages": [
                    sys_msg,
                    HumanMessage(
                        content=(
                            f"Call the tool `remove_from_cart` with args: product_id='{display_id}'. "
                            "Do not call any other tools. Reply briefly."
                        )
                    ),
                ],
                "step_count": 0,
                "request_id": "eval_req_4",
            }
        )
        tool_calls_4 = _extract_tool_calls(out4["messages"])
        rm_calls = [tc for tc in tool_calls_4 if tc.get("name") == "remove_from_cart"]
        assert rm_calls, "Expected the model to call remove_from_cart"
        rm_args = rm_calls[0].get("args") or {}
        assert str(rm_args.get("product_id")) == display_id

        item = (
            db.query(CartItem)
            .filter(CartItem.cart_id == cart.id, CartItem.product_id == mapped_product_id)
            .first()
        )
        assert item is None

        # ---- Turn 5: get cart ----
        out5 = await graph.ainvoke(
            {
                "messages": [sys_msg, HumanMessage(content="Show my cart.")],
                "step_count": 0,
                "request_id": "eval_req_5",
            }
        )
        tool_calls_5 = _extract_tool_calls(out5["messages"])
        assert any(tc.get("name") == "get_cart" for tc in tool_calls_5)

    finally:
        try:
            _clear_session_state(db, session_id)
        finally:
            db.close()
            engine.dispose()


@pytest.mark.asyncio
@pytest.mark.skipif(not _should_run_real_llm_eval(), reason=REAL_LLM_SKIP_REASON)
async def test_real_llm_tool_accuracy_quantity_zero_removes_item():
    """Tool accuracy: updating quantity to 0 should remove the item from the cart in DB."""

    _ensure_real_llm_prereqs_or_skip()
    from backend.app.agent import create_agent_graph

    db_url = os.environ["DATABASE_URL"]
    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    session_id = f"eval_{uuid.uuid4().hex}"
    db = Session()
    try:
        _ensure_seed_products(db)
        _clear_session_state(db, session_id)

        graph = create_agent_graph(db, session_id)
        assert graph is not None

        sys_prompt = get_system_prompt() or {}
        sys_msg = SystemMessage(content=sys_prompt.get("content", ""))

        # Add a known product deterministically by SKU
        out1 = await graph.ainvoke(
            {
                "messages": [
                    sys_msg,
                    HumanMessage(
                        content=(
                            "Call the tool `add_to_cart` with args: product_id='ACC-LOG-MX3S', quantity=1. "
                            "Do not call any other tools. Reply briefly."
                        )
                    ),
                ],
                "step_count": 0,
                "request_id": "eval_q0_1",
            }
        )
        tool_calls_1 = _extract_tool_calls(out1["messages"])
        assert any(tc.get("name") == "add_to_cart" for tc in tool_calls_1)

        cart = db.query(Cart).filter(Cart.session_id == session_id).first()
        assert cart is not None
        assert (
            db.query(CartItem)
            .filter(CartItem.cart_id == cart.id, CartItem.product_id == "ACC-LOG-MX3S")
            .first()
            is not None
        )

        # quantity=0 (tools implementation removes)
        out2 = await graph.ainvoke(
            {
                "messages": [
                    sys_msg,
                    HumanMessage(
                        content=(
                            "Call the tool `update_cart_quantity` with args: product_id='ACC-LOG-MX3S', quantity=0. "
                            "Do not call any other tools. Reply briefly."
                        )
                    ),
                ],
                "step_count": 0,
                "request_id": "eval_q0_2",
            }
        )
        tool_calls_2 = _extract_tool_calls(out2["messages"])
        upd_calls = [tc for tc in tool_calls_2 if tc.get("name") == "update_cart_quantity"]
        assert upd_calls, "Expected update_cart_quantity tool call"
        upd_args = upd_calls[0].get("args") or {}
        assert str(upd_args.get("product_id")) == "ACC-LOG-MX3S"
        assert int(upd_args.get("quantity")) == 0

        # DB should have no item
        assert (
            db.query(CartItem)
            .filter(CartItem.cart_id == cart.id, CartItem.product_id == "ACC-LOG-MX3S")
            .first()
            is None
        )

    finally:
        try:
            _clear_session_state(db, session_id)
        finally:
            db.close()
            engine.dispose()


@pytest.mark.asyncio
@pytest.mark.skipif(not _should_run_real_llm_eval(), reason=REAL_LLM_SKIP_REASON)
async def test_real_llm_tool_accuracy_invalid_display_id_does_not_add():
    """Tool accuracy: invalid display_id should still call add_to_cart but must not create a cart item."""

    _ensure_real_llm_prereqs_or_skip()
    from backend.app.agent import create_agent_graph

    db_url = os.environ["DATABASE_URL"]
    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    session_id = f"eval_{uuid.uuid4().hex}"
    db = Session()
    try:
        _ensure_seed_products(db)
        _clear_session_state(db, session_id)

        graph = create_agent_graph(db, session_id)
        assert graph is not None

        sys_prompt = get_system_prompt() or {}
        sys_msg = SystemMessage(content=sys_prompt.get("content", ""))

        # Ensure the display_id does not exist for this session
        invalid_display_id = "99999"
        assert (
            db.query(SearchResult)
            .filter(SearchResult.session_id == session_id, SearchResult.display_id == int(invalid_display_id))
            .first()
            is None
        )

        out = await graph.ainvoke(
            {
                "messages": [
                    sys_msg,
                    HumanMessage(
                        content=(
                            f"Call the tool `add_to_cart` with args: product_id='{invalid_display_id}', quantity=1. "
                            "Reply briefly after tool execution."
                        )
                    ),
                ],
                "step_count": 0,
                "request_id": "eval_badid_1",
            }
        )
        tool_calls = _extract_tool_calls(out["messages"])
        add_calls = [tc for tc in tool_calls if tc.get("name") == "add_to_cart"]
        assert add_calls, "Expected add_to_cart tool call"
        add_args = add_calls[0].get("args") or {}
        assert str(add_args.get("product_id")) == invalid_display_id

        cart = db.query(Cart).filter(Cart.session_id == session_id).first()
        if cart:
            items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
            assert len(items) == 0

    finally:
        try:
            _clear_session_state(db, session_id)
        finally:
            db.close()
            engine.dispose()


@pytest.mark.asyncio
@pytest.mark.skipif(not _should_run_real_llm_eval(), reason=REAL_LLM_SKIP_REASON)
async def test_real_llm_tool_accuracy_cart_question_calls_get_cart():
    """Tool accuracy: questions about the cart should call get_cart (per system prompt)."""

    _ensure_real_llm_prereqs_or_skip()
    from backend.app.agent import create_agent_graph

    db_url = os.environ["DATABASE_URL"]
    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    session_id = f"eval_{uuid.uuid4().hex}"
    db = Session()
    try:
        _ensure_seed_products(db)
        _clear_session_state(db, session_id)

        graph = create_agent_graph(db, session_id)
        assert graph is not None

        sys_prompt = get_system_prompt() or {}
        sys_msg = SystemMessage(content=sys_prompt.get("content", ""))

        # Put something in cart
        out1 = await graph.ainvoke(
            {
                "messages": [
                    sys_msg,
                    HumanMessage(
                        content=(
                            "Call the tool `add_to_cart` with args: product_id='ACC-LOG-MX3S', quantity=1. "
                            "Do not call any other tools. Reply briefly."
                        )
                    ),
                ],
                "step_count": 0,
                "request_id": "eval_cartq_1",
            }
        )
        assert any(tc.get("name") == "add_to_cart" for tc in _extract_tool_calls(out1["messages"]))

        # Ask about cart: should call get_cart (not hallucinate)
        out2 = await graph.ainvoke(
            {
                "messages": [
                    sys_msg,
                    HumanMessage(
                        content="What is in my cart right now? Use tools to get the latest cart state."
                    ),
                ],
                "step_count": 0,
                "request_id": "eval_cartq_2",
            }
        )
        tool_calls_2 = _extract_tool_calls(out2["messages"])
        assert any(tc.get("name") == "get_cart" for tc in tool_calls_2)

    finally:
        try:
            _clear_session_state(db, session_id)
        finally:
            db.close()
            engine.dispose()
