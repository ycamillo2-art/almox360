from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="USER") # ADMIN, USER

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    category = Column(String)
    stock = Column(Float, default=0.0)
    location = Column(String)
    min_stock = Column(Float, default=0.0)
    observation = Column(String, nullable=True)
    in_use = Column(Float, default=0.0)

class History(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    product_id = Column(Integer, ForeignKey("products.id"))
    type = Column(String) # SAIDA, ENTRADA
    quantity = Column(Float)
    responsible = Column(String)
    previous_stock = Column(Float)
    current_stock = Column(Float)
    location = Column(String)
    synced = Column(Integer, default=1) # 0 para registros que vieram offline e precisam ser validados (opcional)

    product = relationship("Product")
