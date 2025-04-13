from typing import List

import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

from services import get_current_user
from services import get_db, get_user_by_email, create_user, authenticate_user, create_token, create_lead, get_leads, get_lead, delete_lead, update_lead, create_database
from schemas import UserCreateScheme, UserScheme, LeadScheme, LeadCreateScheme

app = FastAPI(lifespan=lambda: create_database())

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://213.108.23.238",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def lifespan(app: FastAPI):
    create_database()
    yield

@app.post("/api/users")
async def user_create(user: UserCreateScheme, db: Session = Depends(get_db)):
    db_user = await get_user_by_email(str(user.email), db)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = await create_user(user, db)

    return await create_token(db_user)

@app.post("/api/token")
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return await create_token(user)

@app.get("/api/users/me", response_model=UserScheme)
async def get_user(user: UserScheme = Depends(get_current_user)):
    return user

@app.post("/api/leads", response_model=LeadScheme)
async def lead_create(lead: LeadCreateScheme, user: UserScheme = Depends(get_current_user), db: Session = Depends(get_db)):
    return await create_lead(user=user, db=db, lead=lead)

@app.get("/api/leads", response_model=List[LeadScheme])
async def leads_get(user: UserScheme = Depends(get_current_user), db: Session = Depends(get_db)):
    return await get_leads(user=user, db=db)

@app.get("/api/leads/{lead_id}", status_code=200)
async def lead_get(lead_id: int, user: UserScheme = Depends(get_current_user), db: Session = Depends(get_db)):
    return await get_lead(lead_id=lead_id, user=user, db=db)

@app.delete("/api/leads/{lead_id}", status_code=204)
async def lead_delete(lead_id: int, user: UserScheme = Depends(get_current_user), db: Session = Depends(get_db)):
    await delete_lead(lead_id=lead_id, user=user, db=db)
    return {"message": "Success: deleted"}

@app.put("/api/leads/{lead_id}", status_code=200)
async def lead_update(lead_id: int, lead: LeadCreateScheme, user: UserScheme = Depends(get_current_user), db: Session = Depends(get_db)):
    await update_lead(lead_id=lead_id, lead=lead, db=db, user=user)
    return {"message": "Success: updated"}

@app.get("/api/welcome")
async def get_api():
    return {"message": "Welcome to the API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)