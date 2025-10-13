"""Database initialization script for Numa.

Creates initial test data for development and testing.
"""

from database import SessionLocal, engine
from models import Base, User

# Create all tables
Base.metadata.create_all(bind=engine)


def create_test_user():
    """Create a test user for development."""
    db = SessionLocal()

    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.email == "test@numa.dev").first()

        if not existing_user:
            test_user = User(email="test@numa.dev", name="Test User")

            db.add(test_user)
            db.commit()
            db.refresh(test_user)

            print(f"✅ Test user created with ID: {test_user.id}")
        else:
            print(f"ℹ️  Test user already exists with ID: {existing_user.id}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error creating test user: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_test_user()
