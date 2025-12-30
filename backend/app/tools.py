from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import Product, Cart, CartItem, SearchResult
from thefuzz import process, fuzz
import random
import json
import uuid

class ShoppingTools:
    def __init__(self, db: Session, session_id: str):
        self.db = db
        self.session_id = session_id

    def _get_cart(self) -> Cart:
        cart = self.db.query(Cart).filter(Cart.session_id == self.session_id).first()
        if not cart:
            cart = Cart(session_id=self.session_id)
            self.db.add(cart)
            self.db.commit()
            self.db.refresh(cart)
        return cart

    def get_cart_summary(self) -> Dict[str, Any]:
        """
        Returns the current state of the shopping cart including items and totals,
        along with a navigation action.
        """
        cart = self._get_cart()
        
        # Query items and join with Product to get details
        items = self.db.query(CartItem, Product).join(
            Product, CartItem.product_id == Product.product_id
        ).filter(
            CartItem.cart_id == cart.id
        ).all()
        
        cart_items = []
        total_cents = 0
        
        for item, product in items:
            item_total = item.quantity * product.price_cents
            total_cents += item_total
            cart_items.append({
                "product_id": product.product_id,
                "name": product.name,
                "quantity": item.quantity,
                "price": product.price_cents / 100.0,
                "total": item_total / 100.0,
                "image_url": product.image_url,
                "category": product.category,
                "brand": product.brand
            })
            
        return {
            "items": cart_items,
            "total": total_cents / 100.0,
            "item_count": sum(item.quantity for item in [i[0] for i in items]),
            "action": "navigate",
            "target": "/cart",
            "message": "Here is your cart."
        }

    def add_to_cart(self, product_id_input: str, quantity: int = 1) -> Dict[str, Any]:
        product_id = self._resolve_product_id(product_id_input)
        cart = self._get_cart()
        product = self.get_product_by_id(product_id)
        
        if not product:
            return {"error": f"Product {product_id_input} not found."}
            
        # Check if item exists in cart
        item = self.db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        ).first()
        
        if item:
            item.quantity += quantity
        else:
            item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity,
                price_at_add=int(product['price'] * 100)
            )
            self.db.add(item)
            
        self.db.commit()
        
        return {
            "action": "add_to_cart",
            "message": f"Added {quantity} x {product['name']} to cart.",
            "added_item": {
                "product_id": product['product_id'],
                "id": product['product_id'], # Frontend expects 'id'
                "name": product['name'],
                "price": product['price'],
                "image_url": self.db.query(Product).filter(Product.product_id == product_id).first().image_url,
                "quantity": quantity,
                "category": product['category'],
                "brand": product['brand']
            }
        }

    def remove_from_cart(self, product_id_input: str) -> Dict[str, Any]:
        product_id = self._resolve_product_id(product_id_input)
        cart = self._get_cart()
        item = self.db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        ).first()
        
        if item:
            self.db.delete(item)
            self.db.commit()
            return {
                "action": "remove_from_cart",
                "product_id": product_id,
                "message": "Removed item from cart."
            }
        
        return {"error": "Item not found in cart."}
        
    def update_cart_quantity(self, product_id_input: str, quantity: int) -> Dict[str, Any]:
        product_id = self._resolve_product_id(product_id_input)
        
        if quantity <= 0:
            return self.remove_from_cart(product_id)
            
        cart = self._get_cart()
        item = self.db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        ).first()
        
        if item:
            item.quantity = quantity
            self.db.commit()
            return {
                "action": "update_cart_quantity",
                "product_id": product_id,
                "quantity": quantity,
                "message": f"Updated quantity to {quantity}."
            }
            
        return {"error": "Item not found in cart."}

    def search_products(self, query: str, min_price: Optional[float] = None, max_price: Optional[float] = None, brand: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for products using fuzzy matching on name, brand, and category.
        Supports filtering by price range, brand, and category.
        Returns a list of dictionaries with product details and a temporary score.
        Assigns a 5-digit display_id to each result for easy user reference.
        """
        # Start with a base query
        stmt = select(Product).filter(Product.is_active == True)

        # Apply filters if provided
        if min_price is not None:
            stmt = stmt.filter(Product.price_cents >= int(min_price * 100))
        if max_price is not None:
            stmt = stmt.filter(Product.price_cents <= int(max_price * 100))
        if brand is not None:
            stmt = stmt.filter(Product.brand.ilike(f"%{brand}%"))
        if category is not None:
            # Map frontend/agent categories to DB categories
            # DB uses singular: 'phone', 'laptop', 'accessory'
            category_map = {
                "phones": "phone",
                "phone": "phone",
                "notebooks": "laptop",
                "notebook": "laptop",
                "laptops": "laptop",
                "laptop": "laptop",
                "accessories": "accessory",
                "accessory": "accessory"
            }
            db_category = category_map.get(category.lower(), category)
            stmt = stmt.filter(Product.category.ilike(f"%{db_category}%"))

        products = self.db.execute(stmt).scalars().all()
        
        query_lower = query.lower()
        results = []
        for product in products:
            # simple scoring based on name match
            name_score = fuzz.partial_ratio(query_lower, product.name.lower())
            brand_score = fuzz.partial_ratio(query_lower, str(product.brand).lower())
            cat_score = fuzz.partial_ratio(query_lower, str(product.category).lower())
            spec_score = fuzz.partial_ratio(query_lower, str(product.specs).lower())
            
            # Weighted score
            final_score = max(name_score, brand_score, cat_score, spec_score)
            
            # If query is empty, we just return filtered results with score 100 (if filters matched)
            if not query.strip():
                final_score = 100
            
            # can add threshold to filter out very poor matches
            # if final_score > 10:  # Threshold
            results.append({
                "product": product,
                "score": final_score
            })
        
        # Sort by score desc
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Take top 5
        top_results = results[:5]
        
        # Format output
        formatted_results = []
        for item in top_results:
            p = item["product"]
            # Generate a temporary 5-digit code. 
            display_id = random.randint(10000, 99999)
            
            # Persist mapping
            mapping = SearchResult(
                session_id=self.session_id,
                display_id=display_id,
                product_id=p.product_id
            )
            self.db.add(mapping)
            
            formatted_results.append({
                "product_id": str(p.product_id), # UUID string
                "display_id": display_id,
                "name": p.name,
                "price": p.price_cents / 100.0,
                "currency": p.currency,
                "category": p.category,
                "brand": p.brand,
                "specs": p.specs,
                "rating": float(p.rating) if p.rating else 0.0
            })
            
        self.db.commit()
        return formatted_results

    def _resolve_product_id(self, id_input: str) -> Optional[str]:
        """
        Resolves a product ID from a potential display_id (5 digits), a direct product_id (UUID/SKU),
        or attempts to find a product by name if the input is likely a name.
        """
        id_input = str(id_input).strip()
        
        # 1. Check if it looks like a display_id (5 digits)
        if id_input.isdigit() and len(id_input) == 5:
            mapping = self.db.query(SearchResult).filter(
                SearchResult.session_id == self.session_id,
                SearchResult.display_id == int(id_input)
            ).order_by(SearchResult.created_at.desc()).first()
            
            if mapping:
                return mapping.product_id
        
        # 2. Check if it matches a product_id directly
        product = self.db.query(Product).filter(Product.product_id == id_input).first()
        if product:
            return product.product_id

        # 3. If not a direct match, try to find by name (case-insensitive exact or close match)
        # Check for exact name match first
        product_by_name = self.db.query(Product).filter(Product.name.ilike(id_input)).first()
        if product_by_name:
            return product_by_name.product_id

        # 4. Fuzzy match as a fallback (using existing search logic but stricter)
        # We reuse the search_products logic but just take the top 1 if score is high enough
        # Note: We can't easily call search_products here without potential circular dependencies or side effects (like generating display_ids)
        # So we'll do a simple fuzzy match here using thefuzz
        
        products = self.db.query(Product).filter(Product.is_active == True).all()
        best_score = 0
        best_match = None
        
        for p in products:
            # Match against name and aliases
            score = fuzz.ratio(id_input.lower(), p.name.lower())
            if p.aliases:
                for alias in p.aliases:
                    alias_score = fuzz.ratio(id_input.lower(), alias.lower())
                    if alias_score > score:
                        score = alias_score
            
            if score > best_score:
                best_score = score
                best_match = p

        # If we have a very high confidence match (>80), use it
        if best_match and best_score > 80:
             return best_match.product_id
        
        # Otherwise return the input as is, and let the caller fail
        return id_input

    def get_product_by_id(self, product_id_input: str) -> Optional[Dict[str, Any]]:
        """Get product details by product_id (SKU) or display_id."""
        product_id = self._resolve_product_id(product_id_input)
        
        product = self.db.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            return None
            
        return {
            "product_id": str(product.product_id),
            "name": product.name,
            "price": product.price_cents / 100.0,
            "currency": product.currency,
            "category": product.category,
            "brand": product.brand,
            "specs": product.specs,
            "rating": float(product.rating) if product.rating else 0.0,
            "description": f"{product.brand} {product.name}"
        }

    def validate_products(self, product_ids: List[str]) -> List[Dict[str, Any]]:
        """Validate multiple product IDs and return their details."""
        products = []
        for pid in product_ids:
            p = self.get_product_by_id(pid)
            if p:
                products.append(p)
        return products

    def sync_cart(self, items: List[Dict[str, Any]]) -> None:
        """
        Synchronize the database cart with the provided list of items.
        This is used to ensure the backend DB matches the frontend state (localStorage).
        """
        cart = self._get_cart()
        
        # Clear existing items
        self.db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        
        # Add new items
        for item in items:
            product_id_input = item.get("product_id") or item.get("id")
            quantity = item.get("quantity", 1)
            
            if not product_id_input:
                continue
                
            product_id = self._resolve_product_id(product_id_input)
            if not product_id:
                continue
                
            product = self.db.query(Product).filter(Product.product_id == product_id).first()
            if product:
                cart_item = CartItem(
                    cart_id=cart.id,
                    product_id=product_id,
                    quantity=quantity,
                    price_at_add=product.price_cents
                )
                self.db.add(cart_item)
        
        self.db.commit()
