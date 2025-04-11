from fastapi import APIRouter, Depends, HTTPException, Header, Security, Form, Response, Cookie, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.user import User
from app.schemas.schemas import UserCreate, Token, UserResponse, UserMe
from app.services.auth import get_password_hash, create_access_token, verify_password, get_current_user, login_user
from app.db.db import get_db
from pydantic import EmailStr
from typing import Optional
from .lab import templates

router = APIRouter()


@router.get("/me/", response_model=UserMe)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


# Специально для Swagger Doc кнопки "Authorize"
@router.post("/oauth/", response_model=UserResponse)
def oauth_login(username: EmailStr = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    result = login_user(db, username, password)
    return result

@router.get("/lk/", response_class=HTMLResponse)
def login_form(request: Request, access_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    print(f"cookie: {access_token}")
    user = get_current_user(access_token, db)
    print(f"user: {user}")
    return templates.TemplateResponse("lk.html", {"user": user, "request": request})





@router.get("/login/", response_class=HTMLResponse)
def login_form():
    return """
    <html>
        <body>
            <h2>Login</h2>
            <form action="/oauth-lk/" method="post">
                <input name="username" placeholder="Username">
                <input name="password" type="password" placeholder="Password">
                <input type="submit">
            </form>
        </body>
    </html>
    """


@router.post("/login/", response_model=UserResponse)
def login(user: UserCreate, db: Session = Depends(get_db)):
    result = login_user(db, user.email, user.password)
    return result

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="access_token")  # Удаляем cookie
    return response


# Специально для Swagger Doc кнопки "Authorize"
@router.post("/oauth-lk/", response_model=UserResponse)
def oauth_login_lk(username: EmailStr = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    result = login_user(db, username, password)
    response = RedirectResponse(url="/lk/", status_code=303)
    response.set_cookie(key="access_token", value=result["access_token"], httponly=True)
    return response



@router.post("/sign-up/", response_model=UserResponse)
def sign_up(user: UserCreate, response:Response, db: Session = Depends(get_db)):
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
    result = UserResponse(id=db_user.id,email=db_user.email,access_token=access_token,token_type="bearer")
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return result


@router.get("/sign-up/", response_class=HTMLResponse)
async def sign_up_form(request: Request):
    return templates.TemplateResponse("create_user.html", {"request": request})


