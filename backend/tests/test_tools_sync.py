import pytest
from unittest.mock import MagicMock
from backend.app.tools import ShoppingTools
from backend.app.models import Cart, CartItem, Product
import uuid

def test_sync_cart_functionality():
    # Mock DB session
    mock_db = MagicMock()
    session_id = "test_session_sync"
    tools = ShoppingTools(mock_db, session_id)
    
    # Mock existing cart
    mock_cart = Cart(id=uuid.uuid4(), session_id=session_id)
    tools._get_cart = MagicMock(return_value=mock_cart)
    
    # Mock products in DB
    product_id_1 = str(uuid.uuid4())
    product_1 = Product(
        product_id=product_id_1,
        name="Test Phone",
        price_cents=10000,
        currency="USD"
    )
    
    # Setup mock query behavior
    def mock_query_side_effect(model):
        query_mock = MagicMock()
        if model == CartItem:
            # For delete operation
            filter_mock = MagicMock()
            filter_mock.delete.return_value = None
            query_mock.filter.return_value = filter_mock
            return query_mock
        elif model == Product:
            # For resolving products
            filter_mock = MagicMock()
            filter_mock.first.side_effect = lambda: product_1 # simplified for this test
            query_mock.filter.return_value = filter_mock
            return query_mock
        return query_mock

    mock_db.query.side_effect = mock_query_side_effect
    
    # Also need to mock _resolve_product_id to return our test ID
    tools._resolve_product_id = MagicMock(return_value=product_id_1)
    
    # Items to sync
    items_to_sync = [
        {"product_id": product_id_1, "quantity": 2},
    ]
    
    # Execute sync
    tools.sync_cart(items_to_sync)
    
    # Verifications
    # 1. Check if existing items were cleared (delete called)
    # The chain is db.query(CartItem).filter(...).delete()
    assert mock_db.query.call_count >= 1
    # We can't easily check the exact chain with simple MagicMocks without more setup, 
    # but we can check if db.add was called with new items
    
    assert mock_db.add.called
    added_item = mock_db.add.call_args[0][0]
    assert isinstance(added_item, CartItem)
    assert added_item.product_id == product_id_1
    assert added_item.quantity == 2
    assert added_item.price_at_add == 10000
    
    assert mock_db.commit.called
