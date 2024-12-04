import subprocess
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from scripts.wait_for_db import wait_for_postgres

def init_database():
    # Wait for the database to be ready
    wait_for_postgres()
    print("Database is ready")
    
    try:
        # Run migrations using the manage_migrations script
        migrations_script = Path(__file__).parent / "manage_migrations.py"
        # Pass current environment variables to the subprocess
        env = os.environ.copy()
        env["PYTHONPATH"] = str(project_root)
        subprocess.run([sys.executable, str(migrations_script)], check=True, env=env)
        print("Database migration completed successfully")
        
    except Exception as e:
        print(f"Error during database initialization: {e}")
        raise

if __name__ == "__main__":
    init_database() 