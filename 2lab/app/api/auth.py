from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.schemas import UserCreate, Token, UserResponse
from app.services.auth import get_password_hash, create_access_token, verify_password
from app.db.db import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login/", response_model=UserResponse)
def login(user: UserCreate, db: Session = Depends(get_db)):
    # Проверяем существует ли пользователь
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Проверяем пароль
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    # Генерируем токен
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "id": db_user.id,
        "email": db_user.email,
        "token": access_token
    }


@router.post("/sign-up/", response_model=UserResponse)
def sign_up(user: UserCreate, db: Session = Depends(get_db)):
    # Проверяем, есть ли уже пользователь с таким email
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Хешируем пароль и сохраняем пользователя
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Генерируем токен
    access_token = create_access_token(data={"sub": user.email})
    
    # Возвращаем ответ с id, email и токеном
    return {
        "id": db_user.id,
        "email": db_user.email,
        "token": access_token,
    }

