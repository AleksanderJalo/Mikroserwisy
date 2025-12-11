from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime

DATABASE_URL = "sqlite:///logs.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class LogDB(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String)
    action = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Logs Service")

class LogCreate(BaseModel):
    user: str
    action: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/logs", response_model=dict)
def create_log(log: LogCreate, db: Session = Depends(get_db)):
    db_log = LogDB(user=log.user, action=log.action)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return {"msg": "Log saved", "id": db_log.id}

@app.get("/logs", response_model=list[LogCreate])
def get_logs(db: Session = Depends(get_db)):
    db_logs = db.query(LogDB).all()
    return [{"user": l.user, "action": l.action} for l in db_logs]
