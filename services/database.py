import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("NEON_DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("NEON_DATABASE_URL environment variable is not set")

def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS label_list (
            label_name TEXT NOT NULL,
            image_url TEXT ,
            company TEXT NOT NULL
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()