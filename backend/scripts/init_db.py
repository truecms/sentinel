import subprocess
import os
import sys
from pathlib import Path
from wait_for_db import wait_for_postgres

def init_database():
    # Wait for database
    wait_for_postgres()
    print("Database is ready")
    
    try:
        # Run migrations using the new script
        migrations_script = Path(__file__).parent / "manage_migrations.py"
        subprocess.run([sys.executable, str(migrations_script)], check=True)
        print("Database initialization completed successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during database initialization: {e}")
        raise

if __name__ == "__main__":
    init_database() 