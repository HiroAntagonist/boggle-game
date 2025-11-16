# ABOUTME: Migration script to add new columns to production Postgres database
# ABOUTME: Adds gamer_tag, is_public, and winner_id columns

from sqlalchemy import text
from src.database import engine

def migrate():
    """Add missing columns to production database."""
    with engine.connect() as conn:
        print("Running database migration...")

        # Add gamer_tag column to users table
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN gamer_tag VARCHAR(20)"))
            conn.commit()
            print("✓ Added gamer_tag column to users table")
        except Exception as e:
            print(f"Note: gamer_tag column may already exist: {e}")
            conn.rollback()

        # Add unique constraint and index on gamer_tag
        try:
            conn.execute(text("ALTER TABLE users ADD CONSTRAINT users_gamer_tag_unique UNIQUE (gamer_tag)"))
            conn.commit()
            print("✓ Added unique constraint on gamer_tag")
        except Exception as e:
            print(f"Note: unique constraint may already exist: {e}")
            conn.rollback()

        try:
            conn.execute(text("CREATE INDEX idx_users_gamer_tag ON users(gamer_tag)"))
            conn.commit()
            print("✓ Created index on gamer_tag")
        except Exception as e:
            print(f"Note: index may already exist: {e}")
            conn.rollback()

        # Add is_public column to games table
        try:
            conn.execute(text("ALTER TABLE games ADD COLUMN is_public BOOLEAN DEFAULT FALSE"))
            conn.commit()
            print("✓ Added is_public column to games table")
        except Exception as e:
            print(f"Note: is_public column may already exist: {e}")
            conn.rollback()

        # Add index on is_public
        try:
            conn.execute(text("CREATE INDEX idx_games_is_public ON games(is_public)"))
            conn.commit()
            print("✓ Created index on is_public")
        except Exception as e:
            print(f"Note: index may already exist: {e}")
            conn.rollback()

        # Add winner_id column to games table
        try:
            conn.execute(text("ALTER TABLE games ADD COLUMN winner_id VARCHAR"))
            conn.commit()
            print("✓ Added winner_id column to games table")
        except Exception as e:
            print(f"Note: winner_id column may already exist: {e}")
            conn.rollback()

        # Add index on winner_id
        try:
            conn.execute(text("CREATE INDEX idx_games_winner_id ON games(winner_id)"))
            conn.commit()
            print("✓ Created index on winner_id")
        except Exception as e:
            print(f"Note: index may already exist: {e}")
            conn.rollback()

        print("✓ Migration complete!")

if __name__ == "__main__":
    migrate()
