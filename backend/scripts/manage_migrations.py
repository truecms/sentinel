import os
import sys
from pathlib import Path
import alembic
from alembic import config as alembic_config

def setup_python_path():
    project_root = Path(__file__).parent.parent.absolute()
    sys.path.insert(0, str(project_root))
    print(f"Added {project_root} to Python path")

def run_migrations():
    setup_python_path()
    
    try:
        # Create versions directory if it doesn't exist
        versions_dir = Path(__file__).parent.parent / "alembic_migrations" / "versions"
        versions_dir.mkdir(parents=True, exist_ok=True)
        
        # Get the alembic.ini path
        alembic_ini = Path(__file__).parent.parent / "alembic.ini"
        print(f"\nLooking for alembic.ini at: {alembic_ini}")
        
        if not alembic_ini.exists():
            raise FileNotFoundError(f"alembic.ini not found at {alembic_ini}")
        
        print("Found alembic.ini")
        
        # Create Alembic configuration
        alembic_cfg = alembic_config.Config(str(alembic_ini))
        print("Created Alembic configuration")
        
        # Run migrations
        alembic.command.upgrade(alembic_cfg, "head")
        print("Migrations completed successfully")

    except Exception as e:
        print(f"\nError during migrations: {e}")
        raise

if __name__ == "__main__":
    run_migrations() 