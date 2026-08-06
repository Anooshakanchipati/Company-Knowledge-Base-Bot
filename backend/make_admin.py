from app.database import SessionLocal
from app.models import User

ADMIN_EMAIL = "anusha@example.com"

database = SessionLocal()

try:
    user = (
        database.query(User)
        .filter(User.email == ADMIN_EMAIL.lower())
        .first()
    )

    if not user:
        print("User not found. Register this email first.")
    else:
        user.role = "admin"
        database.commit()
        print(f"{user.email} is now an admin.")
finally:
    database.close()