"""Database initialization script for Numa.

Creates initial test data for development and testing.
Updated for new authentication system.
"""

from app.database import SessionLocal, engine
from app.models import Base, User
from app.security import get_password_hash

# Create all tables
Base.metadata.create_all(bind=engine)


def create_test_user():
    """Create a test user for development with hashed password."""
    db = SessionLocal()

    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.email == "test@numa.dev").first()

        if not existing_user:
            # Create test user with hashed password
            # Using very short password to avoid bcrypt length issues
            hashed_password = get_password_hash("test")
            test_user = User(
                email="test@numa.dev", 
                name="Test User",
                hashed_password=hashed_password
            )

            db.add(test_user)
            db.commit()
            db.refresh(test_user)

            print(f"✅ Test user created with ID: {test_user.id}")
            print(f"🔑 Email: test@numa.dev")
            print(f"🔑 Password: test")
        else:
            print(f"ℹ️  Test user already exists with ID: {existing_user.id}")
            print(f"🔑 Email: test@numa.dev")
            print(f"🔑 Password: test")

    except Exception as e:
        db.rollback()
        print(f"❌ Error creating test user: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_test_user()
