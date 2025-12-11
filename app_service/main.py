from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import requests
import jwt

DATABASE_URL = "sqlite:///app.db"
GATEWAY_URL = "http://127.0.0.1:8080" 
SECRET_KEY = "abc123456"
ALGORITHM = "HS256"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class OrderDB(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    amount = Column(Integer)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="App Service")

class Order(BaseModel):
    id: int
    title: str
    amount: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def send_log(user: str, action: str):
    try:
        requests.post(f"{GATEWAY_URL}/logs/logs", json={"user": user, "action": action})
    except Exception as e:
        print("Nie wysłano loga:", e)

def verify_token(token: str):
    if not token:
        raise HTTPException(status_code=401, detail="Brak tokena")
    if token.startswith("Bearer "):
        token = token[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Nieprawidłowy token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Nieprawidłowy token")

@app.post("/orders", response_model=Order)
def create_order(order: Order, token: str = Header(None), db: Session = Depends(get_db)):
    username = verify_token(token)
    if db.query(OrderDB).filter(OrderDB.id == order.id).first():
        raise HTTPException(status_code=400, detail="Order ID already exists")
    db_order = OrderDB(id=order.id, title=order.title, amount=order.amount)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    send_log(username, f"Dodano zamówienie {order.title} ({order.amount} szt.)")
    return order

@app.get("/orders", response_model=list[Order])
def get_orders(token: str = Header(None), db: Session = Depends(get_db)):
    username = verify_token(token)
    db_orders = db.query(OrderDB).all()
    send_log(username, "Pobrano wszystkie zamówienia")
    return [Order(id=o.id, title=o.title, amount=o.amount) for o in db_orders]

@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: int, token: str = Header(None), db: Session = Depends(get_db)):
    username = verify_token(token)
    db_order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Zamówienie nie znalezione")
    send_log(username, f"Pobrano zamówienie {db_order.title} ({db_order.amount} szt.)")
    return Order(id=db_order.id, title=db_order.title, amount=db_order.amount)

@app.put("/orders/{order_id}", response_model=Order)
def update_order(order_id: int, order: Order, token: str = Header(None), db: Session = Depends(get_db)):
    username = verify_token(token)
    db_order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Zamówienie nie znalezione")
    db_order.title = order.title
    db_order.amount = order.amount
    db.commit()
    db.refresh(db_order)
    send_log(username, f"Zaktualizowano zamówienie {order.title} ({order.amount} szt.)")
    return Order(id=db_order.id, title=db_order.title, amount=db_order.amount)

@app.delete("/orders/{order_id}")
def delete_order(order_id: int, token: str = Header(None), db: Session = Depends(get_db)):
    username = verify_token(token)
    db_order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Zamówienie nie znalezione")
    db.delete(db_order)
    db.commit()
    send_log(username, f"Usunięto zamówienie {db_order.title} ({db_order.amount} szt.)")
    return {"deleted": True}
