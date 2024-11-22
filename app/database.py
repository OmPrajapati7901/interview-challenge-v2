from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# from ..settings import DB_URL  # Ensure settings.py contains DB_URL

# Create the SQLAlchemy engine
DB_URL='postgresql://postgres:7901@localhost/postgres'
engine = create_engine(DB_URL, echo=True)  # Set echo=True to log SQL statements

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for models


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
