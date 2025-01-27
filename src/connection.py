from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model.sql import base

db_user: str = 'cooluser'
db_port: int = 5432
db_host: str = 'localhost'
db_password: str = 'cool'

# URL for database connection
url: str = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/tasks'

# Create the engine
engine = create_engine(url)
def initDB():
    base.metadata.create_all(bind=engine)

# SessionLocal setup for creating session objects
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        # Test connection to the database
        print("Database connection is successful!")
        yield db
    except Exception as e:
        print("Error: Could not connect to the database.")
        print(f"Details: {str(e)}")
    finally:
        db.close()
        print("Database connection closed.")
