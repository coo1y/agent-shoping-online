import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# Load DATABASE_URL from backend/.env
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
def check_pk():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Query to find primary key column for 'products' table
        sql = """
            SELECT a.attname, format_type(a.atttypid, a.atttypmod) AS data_type
            FROM   pg_index i
            JOIN   pg_attribute a ON a.attrelid = i.indrelid
                                 AND a.attnum = ANY(i.indkey)
            WHERE  i.indrelid = 'public.products'::regclass
            AND    i.indisprimary;
        """
        result = conn.execute(text(sql))
        pk_cols = result.fetchall()
        print(f"Primary Key columns: {pk_cols}")

if __name__ == "__main__":
    check_pk()
