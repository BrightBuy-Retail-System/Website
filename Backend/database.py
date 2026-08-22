# Backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./app.db"  # Creates app.db in Backend folder

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to provide a database session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
