import sys
import pkg_resources

def verify_package(package_name):
    try:
        dist = pkg_resources.get_distribution(package_name.split('.')[0])
        print(f"{package_name} version {dist.version} is installed at {dist.location}")
        
        if '.' in package_name:  # For submodules
            try:
                __import__(package_name)
                print(f"Successfully imported {package_name}")
            except ImportError as e:
                print(f"Warning: Package installed but cannot import {package_name}: {e}")
                return False
        return True
    except pkg_resources.DistributionNotFound:
        print(f"Package {package_name} is not installed")
        return False

required_packages = [
    'fastapi',
    'sqlalchemy',
    'pydantic',
    'alembic'
]

all_successful = True
for package in required_packages:
    if not verify_package(package):
        all_successful = False

# Verify alembic specifically
try:
    import alembic
    import alembic.config
    print("Alembic and its submodules are properly installed")
except ImportError as e:
    print(f"Error importing alembic: {e}")
    all_successful = False

if not all_successful:
    sys.exit(1) 