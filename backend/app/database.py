"""Database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# PostgreSQL connection string format: postgresql://user:password@host:port/database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/bizmail_db"
)

try:
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"Warning: Could not create database engine: {e}")
    print("Application will continue, but database features may not work.")
    print("Please check your DATABASE_URL in .env file and ensure PostgreSQL is running.")
    engine = None
    SessionLocal = None

Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    if engine is None or SessionLocal is None:
        raise RuntimeError("Database is not configured. Please check DATABASE_URL in .env file.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    if engine is None:
        print("Skipping database initialization: engine is not configured")
        return
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables initialized successfully")
        
        # Add generation_time_seconds column if it doesn't exist
        try:
            from sqlalchemy import text
            with engine.begin() as conn:
                check_query = text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='email_messages' 
                    AND column_name='generation_time_seconds'
                """)
                result = conn.execute(check_query)
                exists = result.fetchone() is not None
                
                if not exists:
                    alter_query = text("""
                        ALTER TABLE email_messages 
                        ADD COLUMN generation_time_seconds FLOAT NULL
                    """)
                    conn.execute(alter_query)
                    print("Column 'generation_time_seconds' added successfully!")
        except Exception as e:
            print(f"Warning: Could not add generation_time_seconds column: {e}")
    except Exception as e:
        print(f"Warning: Could not initialize database tables: {e}")
        print("Application will continue, but database features may not work.")
        print("Please check your DATABASE_URL in .env file and ensure PostgreSQL is running.")

