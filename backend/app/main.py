from fastapi import FastAPI                  # the web framework that turns functions into API endpoints

from .database import Base, engine           # Base = our tables' parent/registry; engine = the connection to the db
from . import models                         # importing this runs models.py, which registers all four tables onto Base

# base is the parent all four of our tables inherit from (and it keeps a registry of them)

Base.metadata.create_all(bind=engine)        # build every registered table in the database at engine (live pipe to cortex.db)

app = FastAPI(title="Cortex API")            # create the app; the title just shows up in /docs


@app.get("/")                                # when someone sends a GET request to "/", run the function below
def root():                                  # this function handles that request
    return {"status": "ok", "service": "cortex"}   # return a dict -> FastAPI sends it back as JSON