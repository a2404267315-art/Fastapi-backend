
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
load_dotenv()
db_user=os.environ.get("DATABASE_USER")
db_password=os.environ.get("DATABASE_PASSWORD")
db_host=os.environ.get("DATABASE_HOST")
db_port=os.environ.get("DATABASE_PORT")
db_name=os.environ.get("DATABASE_NAME")
db_url=f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
engine = create_engine(db_url, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
