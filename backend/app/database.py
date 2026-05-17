from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# This is the connection string to our Docker Postgres database
SQLALCHEMY_DATABASE_URL = "postgresql://coclear_user:coclear_password@127.0.0.1:5433/coclear_db"

# Create the SQLAlchemy "Engine" (the core interface to the database)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a SessionLocal class. Each instance of this class will be a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all our models will inherit from
Base = declarative_base()
