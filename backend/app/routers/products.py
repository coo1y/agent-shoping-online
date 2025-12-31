from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database

router = APIRouter(
    prefix="/api/products",
    tags=["products"],
)

@router.post("/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(database.get_db)):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, category: str = None, db: Session = Depends(database.get_db)):
    query = db.query(models.Product)
    if category:
        # Handle plural/singular mismatches
        category_map = {
            "phones": "phone",
            "notebooks": "laptop",
            "laptops": "laptop",
            "accessories": "accessory"
        }
        search_category = category_map.get(category.lower(), category)
        query = query.filter(models.Product.category == search_category)
    products = query.offset(skip).limit(limit).all()
    return products

@router.get("/{product_identifier}", response_model=schemas.Product)
def read_product(product_identifier: str, db: Session = Depends(database.get_db)):
    # Find by product_id string
    product = db.query(models.Product).filter(models.Product.product_id == product_identifier).first()
    
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
