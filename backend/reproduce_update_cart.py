import asyncio
import uuid
from app.database import SessionLocal
from app.agent import run_agent_stream
from app.tools import ShoppingTools, Product, Cart

# Mock the database session
db = SessionLocal()
session_id = str(uuid.uuid4())
tools = ShoppingTools(db, session_id)

async def test_update_quantity_stream():
    print(f"Session ID: {session_id}")
    
    # 1. Add an item first so we have something to update
    # Find a product
    product = db.query(Product).first()
    if not product:
        print("No products in DB")
        return

    print(f"Adding product: {product.name} ({product.product_id})")
    # Manually add to cart to prep state
    tools.add_to_cart(product.product_id, 1)
    
    # 2. Ask agent to update quantity
    # We use a display_id if we can, or just name
    user_message = f"Update the quantity of {product.name} to 3 in my cart."
    messages = [{"role": "user", "content": user_message}]
    
    print(f"\nSending message: {user_message}")
    print("-" * 50)
    
    json_block_found = False
    
    async for chunk in run_agent_stream(messages, db, session_id):
        print(chunk, end="", flush=True)
        if "```json" in chunk and "update_cart_quantity" in chunk:
            json_block_found = True
            
    print("\n" + "-" * 50)
    if json_block_found:
        print("SUCCESS: JSON command block for 'update_cart_quantity' was found in the stream.")
    else:
        print("FAILURE: JSON command block for 'update_cart_quantity' was NOT found.")

if __name__ == "__main__":
    asyncio.run(test_update_quantity_stream())
