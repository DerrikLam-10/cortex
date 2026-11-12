from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# This file sets up everything we need to talk to the database.
# The engine is the actual connection, a session is one back-and-forth
# with the database, and Base is what all our tables get built on top of.

SQLALCHEMY_DATABASE_URL = "sqlite:///./cortex.db"

# Open the connection. For now it's just a local file, cortex.db.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# SessionLocal is a "session factory" — we don't make a session here,
# we set up a cutter so we can stamp out a fresh one whenever we need it.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Every table (Class, Lecture, Topic, Question) will be built on this Base.
Base = declarative_base()

#A fresh database session for each requests so the requests don't get scrambled
#Stamp out a new session, hand it to whoever asked for it and pause until they're done and close the connection
#When multiple things fire at once, this allows them to have their own clean sessions isolating them

def get_db():
    db = SessionLocal()   
    try:
        yield db
    finally:
        db.close()