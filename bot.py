import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import SessionLocal, Student
from api import start_api

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: types.Message):
    # Сохраняем пользователя в базу
    db = SessionLocal()
    user = db.query(Student).filter(Student.tg_id == message.from_user.id).first()
    if not user:
        new_student = Student(tg_id=message.from_user.id, full_name=message.from_user.full_name)
        db.add(new_student)
        db.commit()
    db.close()

    builder = InlineKeyboardBuilder()
    builder.button(text="📋 Список группы", callback_data="list")
    builder.button(text="📅 Расписание", callback_data="schedule")
    builder.button(text="✅ Отметиться", callback_data="attend")
    builder.adjust(1)
    
    await message.answer(
        f"Привет, {message.from_user.first_name}! Я бот-помощник старосты.\n"
        "Выбери действие на кнопках ниже:",
        reply_markup=builder.as_markup()
    )

@dp.callback_query()
async def handle_buttons(callback: types.CallbackQuery):
    if callback.data == "list":
        db = SessionLocal()
        students = db.query(Student).all()
        db.close()
        
        text = "Список группы:\n"
        if not students:
            text += "Пока никого нет. Нажмите /start, чтобы добавиться."
        else:
            for i, s in enumerate(students, 1):
                text += f"{i}. {s.full_name}\n"
        await callback.message.answer(text)
        
    elif callback.data == "schedule":
        await callback.message.answer("Расписание: (здесь будет расписание)")
    elif callback.data == "attend":
        await callback.message.answer("Ты отметился на паре! ✅")
    
    await callback.answer()

# Крошечный сервер для Render, чтобы он не выключал бота
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

start_api()
threading.Thread(target=run_server, daemon=True).start()

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
