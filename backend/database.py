from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

#DATABASE_URL = "sqlite:///./database.db"
#engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)

engine = create_engine(settings.DATABASE_URL_psycopg, echo=settings.DEBUG)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
