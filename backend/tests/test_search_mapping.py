from unittest.mock import MagicMock
from backend.app.tools import ShoppingTools

def test_search_category_mapping_logic():
    # Mock DB session
    mock_db = MagicMock()
    # We pass a dummy session_id
    tools = ShoppingTools(mock_db, "test_session")
    
    # Setup mock to capture the statement passed to execute
    def capture_execute(stmt):
        return MagicMock() # return a mock result proxy

    mock_db.execute.side_effect = capture_execute
    
    # --- Test "notebooks" (plural/legacy) -> "laptop" (DB singular) ---
    tools.search_products(query="test", category="notebooks")
    
    call_args = mock_db.execute.call_args
    assert call_args is not None
    stmt = call_args[0][0]
    
    compiled_sql = str(stmt.compile(compile_kwargs={"literal_binds": True}))
    print(f"SQL for notebooks: {compiled_sql}")
    assert "laptop" in compiled_sql
    assert "notebooks" not in compiled_sql

    # --- Test "laptop" (singular) -> "laptop" (identity) ---
    tools.search_products(query="test", category="laptop")
    stmt = mock_db.execute.call_args[0][0]
    compiled_sql = str(stmt.compile(compile_kwargs={"literal_binds": True}))
    print(f"SQL for laptop: {compiled_sql}")
    assert "laptop" in compiled_sql

    # --- Test "accessories" (plural) -> "accessory" (DB singular) ---
    tools.search_products(query="test", category="accessories")
    stmt = mock_db.execute.call_args[0][0]
    compiled_sql = str(stmt.compile(compile_kwargs={"literal_binds": True}))
    print(f"SQL for accessories: {compiled_sql}")
    assert "accessory" in compiled_sql
    
    # --- Test "phones" (plural) -> "phone" (DB singular) ---
    tools.search_products(query="test", category="phones")
    stmt = mock_db.execute.call_args[0][0]
    compiled_sql = str(stmt.compile(compile_kwargs={"literal_binds": True}))
    print(f"SQL for phones: {compiled_sql}")
    assert "phone" in compiled_sql
    assert "phones" not in compiled_sql

    # --- Test unmapped (e.g. "other") ---
    tools.search_products(query="test", category="other")
    stmt = mock_db.execute.call_args[0][0]
    compiled_sql = str(stmt.compile(compile_kwargs={"literal_binds": True}))
    print(f"SQL for other: {compiled_sql}")
    assert "other" in compiled_sql
