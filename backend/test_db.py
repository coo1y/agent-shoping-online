from app.database import SessionLocal
from app import models
import sys

try:
    db = SessionLocal()
    print("Database connection successful.")
    
    count = db.query(models.Product).count()
    print(f"Product count: {count}")
    
    if count > 0:
        product = db.query(models.Product).first()
        print(f"First product ID: {product.id}")
        print(f"First product Name: {product.name}")
        print(f"First product Category: {product.category}")
        
        # Check unique categories
        categories = db.query(models.Product.category).distinct().all()
        print(f"Unique categories in DB: {[c[0] for c in categories]}")
    else:
        print("No products found in DB.")
        
    db.close()
except Exception as e:
    print(f"Error querying database: {e}")
    sys.exit(1)
