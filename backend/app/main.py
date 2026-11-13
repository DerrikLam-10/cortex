from fastapi import FastAPI, Depends, HTTPException          # Depends = how FastAPI hands us the db session
from sqlalchemy.orm import Session             # the type of thing get_db yields — just for clarity

from .database import Base, engine, get_db     # grab get_db now too
from . import models, schemas                  # schemas = the in/out shapes we defined

# base is the parent all four of our tables inherit from (and it keeps a registry of them)

Base.metadata.create_all(bind=engine)        # build every registered table in the database at engine (live pipe to cortex.db)

app = FastAPI(title="Cortex API")            # create the app; the title just shows up in /docs


@app.get("/")                                # when someone sends a GET request to "/", run the function below
def root():                                  # this function handles that request
    return {"status": "ok", "service": "cortex"}   # return a dict -> FastAPI sends it back as JSON


#storage for the courses entered into cortex
@app.post("/classes", response_model=schemas.ClassOut)
def create_class(payload: schemas.ClassCreate, db: Session = Depends(get_db)):
    new_class = models.Class(name=payload.name, code=payload.code)
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class

# list every course the user has added
@app.get("/classes", response_model=list[schemas.ClassOut])
def list_classes(db: Session = Depends(get_db)):          # borrow a clean db session like before
    return db.query(models.Class).all()                   # grab every row in the classes table, hand them all back


# fetch one course by its id
@app.get("/classes/{class_id}", response_model=schemas.ClassOut)
def get_class(class_id: int, db: Session = Depends(get_db)):                     # class_id is pulled straight from the url
    found = db.query(models.Class).filter(models.Class.id == class_id).first()  # look for the row whose id matches
    if found is None:                                                           # nothing in the table had that id
        raise HTTPException(status_code=404, detail="Class not found")          # tell the client it doesn't exist
    return found                                                                # otherwise hand back that one course
