from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from .database import engine, Base
from .routers import products, chat
from .limiter import limiter
import os

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TechShop API")

# Configure Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Configure CORS

cors_origins_env = os.getenv("CORS_ALLOW_ORIGINS")
allow_origins = ["http://localhost:3000"]
if cors_origins_env:
    allow_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(chat.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to TechShop API"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
