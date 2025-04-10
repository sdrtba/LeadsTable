from datetime import datetime
from pydantic import BaseModel

class UserBaseScheme(BaseModel):
    email: str

class UserCreateScheme(UserBaseScheme):
    hashed_password: str

    class Config:
        from_attributes = True

class UserScheme(UserBaseScheme):
    id: int

    class Config:
        from_attributes = True

class LeadBaseScheme(BaseModel):
    first_name: str
    last_name: str
    email: str
    company: str
    note: str

class LeadCreateScheme(LeadBaseScheme):
    pass

class LeadScheme(LeadBaseScheme):
    id: int
    owner_id: int
    date_created: datetime
    date_last_updated: datetime

    class Config:
        from_attributes = True