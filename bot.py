import asyncio
import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import SessionLocal, Student
import uvicorn

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

# --- 1. API для Mini App ---
@app.get("/api/students")
def get_students():
    db = SessionLocal()
    students = db.query(Student).all()
    db.close()
    return [{"id": s.id, "name": s.full_name, "status": s.status} for s in students]

@app.get("/api/stats")
def get_stats():
    db = SessionLocal()
    total = db.query(Student).count()
    db.close()
    return {"total": total, "present": 0, "late": 0, "absent": 0}

@app.get("/")
def read_root():
    return {"status": "alive"}

# --- 2. Логика Бота ---
@dp.message(CommandStart())
async def start(message: types.Message):
    db = SessionLocal()
    user = db.query(Student).filter(Student.tg_id == message.from_user.id).first()
    if not user:
        new_student = Student(tg_id=message.from_user.id, full_name=message.from_user.full_name)
        db.add(new_student)
        db.commit()
    db.close()

    builder = InlineKeyboardBuilder()
    builder.button(text="📋 Список группы", callback_data="list")
    builder.adjust(1)
    await message.answer(f"Привет, {message.from_user.first_name}! Бот работает.", reply_markup=builder.as_markup())

@dp.callback_query()
async def handle_buttons(callback: types.CallbackQuery):
    if callback.data == "list":
        db = SessionLocal()
        students = db.query(Student).all()
        db.close()
        text = "Список группы:\n"
        if not students:
            text += "Пока никого нет."
        else:
            for i, s in enumerate(students, 1):
                text += f"{i}. {s.full_name}\n"
        await callback.message.answer(text)
    await callback.answer()

# --- 3. Webhook (прием сообщений от Telegram) ---
@app.post(f"/webhook/{BOT_TOKEN}")
async def webhook(request: Request):
    update = await request.json()
    telegram_update = types.Update(**update)
    await dp.feed_update(bot, telegram_update)
    return {"ok": True}

# --- 4. Установка Webhook при запуске ---
@app.on_event("startup")
async def on_startup():
    # Ваша ссылка на Render (обязательно проверьте, чтобы она была актуальной!)
    webhook_url = f"https://starosta-bot-jdgg.onrender.com/webhook/{BOT_TOKEN}"
    await bot.set_webhook(webhook_url, drop_pending_updates=True)
    print(f"Webhook установлен: {webhook_url}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
