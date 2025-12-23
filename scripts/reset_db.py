"""Database Reset Script.

This script will delete the existing SQLite database file and recreate it
with the current schema defined in the models.

Run this script from the project root directory:
python -m scripts.reset_db
"""

import os
import sys

# Add the project root to the Python path to allow imports from src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.core.database import engine, Base
from src.modules.finance_core.models import User, Transaction

DB_FILE = "numa_local.db"

def reset_database():
    """Deletes and recreates the database."""
    print("--- Database Reset Utility ---")

    # 1. Delete the old database file
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
            print(f"Successfully deleted old database file: {DB_FILE}")
        except OSError as e:
            print(f"Error: Could not delete file {DB_FILE}. Reason: {e}")
            sys.exit(1)
    else:
        print("No old database file found. A new one will be created.")

    # 2. Recreate the database with the new schema
    try:
        print("Creating new database with updated schema...")
        # This command creates all tables defined by models that inherit from Base
        Base.metadata.create_all(bind=engine)
        print("Successfully created new database and tables.")
        print("\nSchema recreated successfully. You can now run the main application.")
    except Exception as e:
        print(f"Error: Could not create database tables. Reason: {e}")
        sys.exit(1)

if __name__ == "__main__":
    reset_database()
