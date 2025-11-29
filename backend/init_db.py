"""Script to initialize database tables."""

from app.database import init_db, engine
from app.db_models import Base
from sqlalchemy import text

def add_generation_time_column_if_needed():
    """Add generation_time_seconds column to email_messages table if it doesn't exist."""
    try:
        with engine.begin() as conn:
            # Check if column exists
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='email_messages' 
                AND column_name='generation_time_seconds'
            """)
            result = conn.execute(check_query)
            exists = result.fetchone() is not None
            
            if not exists:
                # Add column
                alter_query = text("""
                    ALTER TABLE email_messages 
                    ADD COLUMN generation_time_seconds FLOAT NULL
                """)
                conn.execute(alter_query)
                print("Column 'generation_time_seconds' added successfully!")
    except Exception as e:
        print(f"Warning: Could not add generation_time_seconds column: {e}")

if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    print("Adding generation_time_seconds column if needed...")
    add_generation_time_column_if_needed()
    print("Done!")

