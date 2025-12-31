import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import reflection
from dotenv import load_dotenv
from pathlib import Path

# Load DATABASE_URL from backend/.env
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def inspect_db():
    print(f"Connecting to {DATABASE_URL}...")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            print("Successfully connected!")
            
            # Check for products table
            result = connection.execute(text("SELECT to_regclass('public.products')"))
            table_exists = result.scalar()
            
            if not table_exists:
                print("Table 'products' does NOT exist in public schema.")
                # List all tables
                result = connection.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
                tables = [row[0] for row in result]
                print(f"Tables found: {tables}")
                return

            print("Table 'products' exists.")
            
            # Get columns
            result = connection.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'products'"))
            columns = [(row[0], row[1]) for row in result]
            
            print("\nColumns in 'products':")
            for col_name, data_type in columns:
                print(f"- {col_name}: {data_type}")
                
            # Sample data
            print("\nSample row:")
            result = connection.execute(text("SELECT * FROM products LIMIT 1"))
            row = result.mappings().first()
            if row:
                print(dict(row))
            else:
                print("Table is empty.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_db()
