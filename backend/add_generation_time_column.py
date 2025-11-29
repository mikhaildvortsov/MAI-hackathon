"""Script to add generation_time_seconds column to email_messages table."""

from app.database import engine
from sqlalchemy import text

def add_generation_time_column():
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
            else:
                print("Column 'generation_time_seconds' already exists.")
    except Exception as e:
        print(f"Error adding column: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Adding generation_time_seconds column...")
    add_generation_time_column()
    print("Done!")

