from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from config.database import get_db

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/db-test")
def db_test(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1"))
        return {
            "database": "connected",
            "result": result.scalar()
        }
    except Exception as e:
        return {
            "database": "not connected",
            "error": str(e)
        }