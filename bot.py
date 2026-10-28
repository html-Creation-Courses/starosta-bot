import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Токен будет браться из настроек хостинга
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: types.Message):
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

# Обработка нажатий на кнопки
@dp.callback_query()
async def handle_buttons(callback: types.CallbackQuery):
    if callback.data == "list":
        await callback.message.answer("Список студентов: (здесь будет список)")
    elif callback.data == "schedule":
        await callback.message.answer("Расписание: (здесь будет расписание)")
    elif callback.data == "attend":
        await callback.message.answer("Ты отметился на паре! ✅")
    
    await callback.answer()

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

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

# Запускаем сервер в фоне перед стартом бота
threading.Thread(target=run_server, daemon=True).start()

if __name__ == "__main__":
    asyncio.run(main())
