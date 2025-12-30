from app.database import SessionLocal, engine, Base
from app import models
import datetime

from sqlalchemy import text

def seed_data():
    # Create tables if they don't exist
    print("Creating tables (if not exist)...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Check if data already exists
    if db.query(models.Product).count() > 0:
        print("Data already exists. Skipping seed.")
        db.close()
        return

    products = [
        models.Product(
            product_id="PHN-APL-IPH15P",
            name="iPhone 15 Pro",
            brand="Apple",
            price_cents=99900,
            category="phone",
            image_url="https://images.unsplash.com/photo-1696446701796-da61225697cc?q=80&w=1000&auto=format&fit=crop",
            popularity=150,
            rating=4.8,
            specs={"chip": "A17 Pro", "display": "6.1-inch", "storage": "128GB"},
            aliases=["iphone15pro", "ip15p"]
        ),
        models.Product(
            product_id="NB-APL-MBP14-M3",
            name="MacBook Pro 14",
            brand="Apple",
            price_cents=159900,
            category="laptop",
            image_url="https://images.unsplash.com/photo-1517336714731-489689fd1ca4?q=80&w=1000&auto=format&fit=crop",
            popularity=200,
            rating=4.9,
            specs={"chip": "M3", "ram": "8GB", "storage": "512GB"},
            aliases=["mbp14", "macbookpro"]
        ),
        models.Product(
            product_id="ACC-SNY-WH1000XM5",
            name="Sony WH-1000XM5",
            brand="Sony",
            price_cents=34800,
            category="accessory",
            image_url="https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?q=80&w=1000&auto=format&fit=crop",
            popularity=120,
            rating=4.7,
            specs={"type": "Over-ear", "noise_cancelling": True, "battery_life": "30h"},
            aliases=["sony headphones", "xm5"]
        ),
        models.Product(
            product_id="PHN-SMS-S24U",
            name="Samsung Galaxy S24 Ultra",
            brand="Samsung",
            price_cents=129900,
            category="phone",
            image_url="https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?q=80&w=1000&auto=format&fit=crop",
            popularity=180,
            rating=4.8,
            specs={"chip": "Snapdragon 8 Gen 3", "display": "6.8-inch", "pen": "S Pen included"},
            aliases=["s24ultra", "galaxy s24"]
        ),
        models.Product(
            product_id="NB-DEL-XPS13",
            name="Dell XPS 13",
            brand="Dell",
            price_cents=109900,
            category="laptop",
            image_url="https://images.unsplash.com/photo-1593642632823-8f78536788c6?q=80&w=1000&auto=format&fit=crop",
            popularity=80,
            rating=4.5,
            specs={"processor": "Intel Core i7", "ram": "16GB", "storage": "512GB"},
            aliases=["xps13", "dell laptop"]
        ),
        models.Product(
            product_id="ACC-APL-APP2",
            name="AirPods Pro (2nd Gen)",
            brand="Apple",
            price_cents=24900,
            category="accessory",
            image_url="https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?q=80&w=1000&auto=format&fit=crop",
            popularity=300,
            rating=4.8,
            specs={"type": "In-ear", "noise_cancelling": True, "connector": "USB-C"},
            aliases=["airpods", "app2"]
        ),
        models.Product(
            product_id="NB-APL-IPA",
            name="iPad Air",
            brand="Apple",
            price_cents=59900,
            category="laptop",
            image_url="https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?q=80&w=1000&auto=format&fit=crop",
            popularity=90,
            rating=4.6,
            specs={"chip": "M1", "display": "10.9-inch", "storage": "64GB"},
            aliases=["ipad", "ipad air"]
        ),
        models.Product(
            product_id="PHN-GGL-PXL8",
            name="Google Pixel 8",
            brand="Google",
            price_cents=69900,
            category="phone",
            image_url="https://images.unsplash.com/photo-1598327773507-741081395abc?q=80&w=1000&auto=format&fit=crop",
            popularity=70,
            rating=4.4,
            specs={"chip": "Tensor G3", "display": "6.2-inch", "camera": "50MP Main"},
            aliases=["pixel8", "google phone"]
        ),
        models.Product(
            product_id="ACC-LOG-MX3S",
            name="Logitech MX Master 3S",
            brand="Logitech",
            price_cents=9900,
            category="accessory",
            image_url="https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?q=80&w=1000&auto=format&fit=crop",
            popularity=110,
            rating=4.9,
            specs={"dpi": "8000", "connectivity": "Bluetooth/Bolt", "buttons": 7},
            aliases=["mx master", "logitech mouse"]
        ),
    ]

    for product in products:
        db.add(product)
    
    db.commit()
    print("Database seeded successfully!")
    db.close()

if __name__ == "__main__":
    seed_data()
