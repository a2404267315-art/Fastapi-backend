from .database_structure import Base
from .engine_creating import SessionLocal
import time

def init_db(engine):
    print(f"Connecting to database")
    
    max_retries = 30
    wait_seconds = 2

    for i in range(max_retries):
        try:
            Base.metadata.create_all(engine)
            return
        except Exception as e:
            print(f"Attempt {i+1}/{max_retries} failed: Database not ready yet. Retrying in {wait_seconds}s...")
            print(f"Error details: {e}")
            time.sleep(wait_seconds)
    raise Exception("Database connection failed after retries")

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()