import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from services import get_current_user
from services import get_db, get_user_by_email, create_user, authenticate_user, create_token
from schemas import UserCreateScheme, UserScheme

app = FastAPI()

@app.post("/api/users")
async def user_create(user: UserCreateScheme, db: Session = Depends(get_db)):
    db_user = await get_user_by_email(user.email, db)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    return await create_user(user, db)

@app.post("/api/token")
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return await create_token(user)

@app.get("/api/users/me", response_model=UserScheme)
async def get_user(user: UserScheme = Depends(get_current_user)):
    return user


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3001, reload=True)