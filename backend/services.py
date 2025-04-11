from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import User, Lead
from schemas import UserCreateScheme, UserScheme, LeadCreateScheme, LeadScheme
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

async def create_lead(user: UserScheme, db: Session, lead: LeadCreateScheme):
    lead = Lead(**lead.model_dump(), owner_id=user.id)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return LeadScheme.model_validate(lead)


async def get_leads(user: UserScheme, db: Session):
    leads = db.query(Lead).filter_by(owner_id=user.id)
    return list(map(LeadScheme.model_validate, leads))

async def _lead_selector(lead_id: int, user: UserScheme, db: Session):
    lead = db.query(Lead).filter_by(owner_id=user.id).filter(Lead.id == lead_id).first()

    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")

    return lead

async def get_lead(lead_id: int, user: UserScheme, db: Session):
    lead = await _lead_selector(lead_id, user, db)
    return LeadScheme.model_validate(lead)

async def delete_lead(lead_id: int, user: UserScheme, db: Session):
    lead = await _lead_selector(lead_id, user, db)

    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")

    db.delete(lead)
    db.commit()


async def update_lead(lead_id: int, lead:LeadCreateScheme, user: UserScheme, db: Session):
    lead_db = await _lead_selector(lead_id, user, db)

    lead_db.first_name = lead.first_name
    lead_db.last_name = lead.last_name
    lead_db.email = lead.email
    lead_db.company = lead.company
    lead_db.note = lead.note
    lead_db.date_last_updated = datetime.datetime.now(datetime.timezone.utc)

    db.commit()
    db.refresh(lead_db)

    return LeadScheme.model_validate(lead_db)