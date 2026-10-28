import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Берем ссылку на базу из настроек Render
DATABASE_URL = os.getenv("DATABASE_URL")

# Если ссылка начинается с postgres://, меняем на postgresql:// (требование SQLAlchemy)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Таблица для студентов
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(Integer, unique=True)
    full_name = Column(String)
    status = Column(String, default="active") # active, late, absent

# Создаем таблицы (если их нет)
Base.metadata.create_all(bind=engine)
