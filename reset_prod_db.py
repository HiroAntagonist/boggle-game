#!/usr/bin/env python3
# ABOUTME: Database reset script for production PostgreSQL database.
# ABOUTME: Connects via Fly.io proxy to reset the remote database.

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Force PostgreSQL connection via proxy
os.environ["DATABASE_URL"] = "postgresql://postgres:your_password@localhost:15432/boggle"

from src.database import Base, engine
from src.models import User, Game, GamePlayer  # Import all models


def reset_database() -> None:
    """Drop all tables and recreate them from models.

    WARNING: This will DELETE ALL DATA in the database!
    """
    print("WARNING: This will delete all data in the PRODUCTION database!")
    print(f"Database: {engine.url}")

    response = input("Are you sure you want to continue? (yes/no): ")
    if response.lower() != "yes":
        print("Aborted.")
        sys.exit(0)

    print("\nDropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("✓ All tables dropped")

    print("\nCreating all tables from models...")
    Base.metadata.create_all(bind=engine)
    print("✓ All tables created")

    print("\n✅ Database reset complete!")


if __name__ == "__main__":
    reset_database()
