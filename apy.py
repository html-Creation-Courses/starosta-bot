from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, Student
import uvicorn
import threading

app = FastAPI()

# Разрешаем Mini App делать запросы к этому серверу
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/students")
def get_students():
    db = SessionLocal()
    students = db.query(Student).all()
    db.close()
    # Возвращаем список студентов в формате JSON для Mini App
    return [{"id": s.id, "name": s.full_name, "status": s.status} for s in students]

@app.get("/api/stats")
def get_stats():
    db = SessionLocal()
    total = db.query(Student).count()
    db.close()
    return {"total": total, "present": 0, "late": 0, "absent": 0}

def run_api():
    # Запускаем API на порту 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Запускаем API в фоновом потоке при старте
def start_api():
    threading.Thread(target=run_api, daemon=True).start()
