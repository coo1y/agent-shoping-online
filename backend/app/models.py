from sqlalchemy import Column, Integer, String, Boolean, DateTime, ARRAY, JSON, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .database import Base
import datetime

class Product(Base):
    __tablename__ = "products"

    # internal stable id (use String for VARCHAR)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(String, unique=True, index=True) 
    name = Column(String, index=True)
    brand = Column(String)
    category = Column(String, index=True)
    
    price_cents = Column(Integer)
    currency = Column(String, default='USD')
    
    aliases = Column(ARRAY(String), default=[])
    specs = Column(JSON, default={})
    
    rating = Column(Numeric(2, 1))
    popularity = Column(Integer, default=0)
    
    image_url = Column(String)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Cart(Base):
    __tablename__ = "carts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    # For now, we can treat a single cart or identify by some session_id if needed.
    # In this demo, we might just have one active cart or create one per new session.
    session_id = Column(String, unique=True, index=True)

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_id = Column(UUID(as_uuid=True), index=True)
    product_id = Column(String) # Store the SKU
    quantity = Column(Integer, default=1)
    
    # Snapshot of price at time of add, optional, but good practice
    price_at_add = Column(Integer) 

class SearchResult(Base):
    __tablename__ = "search_results"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    display_id = Column(Integer)
    product_id = Column(String) # The actual UUID string
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


