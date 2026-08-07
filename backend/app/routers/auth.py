import os

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_database
from app.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: schemas.UserRegister,
    database: Session = Depends(get_database),
):
    normalized_email = user_data.email.strip().lower()

    existing_user = (
        database.query(models.User)
        .filter(models.User.email == normalized_email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    admin_email = os.getenv(
        "ADMIN_EMAIL",
        "",
    ).strip().lower()

    new_user = models.User(
        name=user_data.name.strip(),
        email=normalized_email,
        password=hash_password(user_data.password),
        role=(
            "admin"
            if normalized_email == admin_email
            else "user"
        ),
    )

    database.add(new_user)
    database.commit()
    database.refresh(new_user)

    return new_user


@router.post(
    "/login",
    response_model=schemas.TokenResponse,
)
def login_user(
    login_data: schemas.UserLogin,
    database: Session = Depends(get_database),
):
    normalized_email = login_data.email.strip().lower()

    user = (
        database.query(models.User)
        .filter(models.User.email == normalized_email)
        .first()
    )

    if not user or not verify_password(
        login_data.password,
        user.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Make the configured account an admin.
    # This also updates an account registered before ADMIN_EMAIL was added.
    admin_email = os.getenv(
        "ADMIN_EMAIL",
        "",
    ).strip().lower()

    if user.email == admin_email and user.role != "admin":
        user.role = "admin"
        database.commit()
        database.refresh(user)

    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


@router.get(
    "/me",
    response_model=schemas.UserResponse,
)
def get_logged_in_user(
    current_user: models.User = Depends(get_current_user),
):
    return current_user