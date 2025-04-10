from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import User
from schemas import UserCreateScheme, UserScheme
from passlib.hash import bcrypt
from config import settings
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import datetime
import jwt

oauth2schema = OAuth2PasswordBearer(tokenUrl="/api/token")

def create_database():
    return Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_user_by_email(email: str, db: Session):
    return db.query(User).filter(User.email == email).first()

async def create_user(user: UserCreateScheme, db: Session):
    user_obj = User(email=str(user.email), hashed_password=bcrypt.hash(user.password))
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

async def authenticate_user(email: str, password: str, db: Session):
    user = await get_user_by_email(email, db)
    if not user:
        return False
    if not user.verify_password(password):
        return False

    return user

async def create_token(user: User):
    token_payload = {
        "id": user.id,
        "email": user.email,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=settings.TOKEN_EXPIRATION_MINUTES)
    }

    token = jwt.encode(token_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return dict(access_token=token, token_type="Bearer")

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2schema)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user = db.get(User, payload["id"])
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user