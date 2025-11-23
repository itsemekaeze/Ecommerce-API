from sqlalchemy.orm import Session
from src.entities.users import User, UserRole
from src.auth.service import get_hashed_password
from dotenv import dotenv_values

config = dotenv_values(".env")


def create_default_admin(db: Session) -> User | None:
    """Create default admin user if it doesn't exist"""
    
    admin_email = config.get("ADMIN_EMAIL", "admin@ecommerce.com")
    admin_password = config.get("ADMIN_PASSWORD", "Admin@123456!")
    admin_username = config.get("ADMIN_USERNAME", "admin")
    
    # Check if ANY admin already exists (not just the default one)
    existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    
    if existing_admin:
        print(f"Admin already exists: {existing_admin.email} - Skipping admin creation")
        return None
    
    # Also check if the specific email/username is taken
    existing_user = db.query(User).filter(
        (User.email == admin_email) | (User.username == admin_username)
    ).first()
    
    if existing_admin:
        print(f"ℹ️  Admin user already exists: {admin_email}")
        return existing_admin
    
    # Create admin user
    admin_user = User(
        email=admin_email,
        username=admin_username,
        hashed_password=get_hashed_password(admin_password),
        full_name="System Administrator",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True 
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    print(f"Default admin created successfully!")
    print(f"Email: {admin_email}")
    print(f"Username: {admin_username}")
    print(f"Password: {admin_password}")
    print(f"Please change the password after first login!")
    
    return admin_user


def init_db(db: Session):
    """Initialize database with default data"""
    print("\n Initializing database...")
    
    create_default_admin(db)

    print("✅ Database initialization complete!")