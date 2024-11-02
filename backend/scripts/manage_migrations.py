import os
import sys
from pathlib import Path

def setup_python_path():
    # Add the project root to Python path
    project_root = Path(__file__).parent.parent.absolute()
    sys.path.insert(0, str(project_root))
    print(f"Added {project_root} to Python path")
    print(f"Current Python path: {sys.path}")

def run_migrations():
    setup_python_path()
    
    try:
        # Print Python package information
        import pkg_resources
        print("\nInstalled packages:")
        for pkg in pkg_resources.working_set:
            print(f"{pkg.key} {pkg.version}")
        
        print("\nTrying to import alembic...")
        import alembic
        print(f"Alembic imported from: {alembic.__file__}")
        
        print("\nTrying to import alembic.config...")
        import alembic.config
        print("Successfully imported alembic.config")
        
        # Get the alembic.ini path
        alembic_ini = Path(__file__).parent.parent / "alembic.ini"
        print(f"\nLooking for alembic.ini at: {alembic_ini}")
        if not alembic_ini.exists():
            raise FileNotFoundError(f"alembic.ini not found at {alembic_ini}")
        
        print("Found alembic.ini")
        
        # Create Alembic configuration
        alembic_cfg = alembic.config.Config(str(alembic_ini))
        print("Created Alembic configuration")
        
        # Create initial migration
        try:
            alembic.command.revision(alembic_cfg, autogenerate=True, message="Initial migration")
            print("Created initial migration")
        except Exception as e:
            print(f"Note: {e}")
        
        # Run migrations
        alembic.command.upgrade(alembic_cfg, "head")
        print("Migrations completed successfully")
        
    except Exception as e:
        print(f"\nError during migrations: {e}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Directory contents: {os.listdir()}")
        print("\nPython sys.path:")
        for p in sys.path:
            print(f"  {p}")
        raise

if __name__ == "__main__":
    run_migrations() 