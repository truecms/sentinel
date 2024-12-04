import subprocess
import os
import sys
from pathlib import Path
from wait_for_db import wait_for_postgres
from app.database import init_db

def init_database():
    # Wait for database
    wait_for_postgres()
    print("Database is ready")
    
    try:
        # Create tables directly using SQLAlchemy
        init_db()
        print("Created database tables")
        
        # Run migrations using the manage_migrations script
        migrations_script = Path(__file__).parent / "manage_migrations.py"
        subprocess.run([sys.executable, str(migrations_script)], check=True)
        print("Database initialization completed successfully")
        
    except Exception as e:
        print(f"Error during database initialization: {e}")
        raise

if __name__ == "__main__":
    init_database() 