from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import asyncio
import requests
import json
from instagrapi import Client

# Telegram bot tokeni
TOKEN = "SIZNING_TELEGRAM_BOT_TOKEN"
ADMIN_ID = "SIZNING_TELEGRAM_ID"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

cl = Client()
SESSION_PATH = "session/session.json"

# Fikr yozish sozlamalari
comment_text = "Standart izoh"
post_url = "POST_URL"
comment_interval = 300  # 5 daqiqa (sekund)

async def comment_loop():
    global comment_text, post_url, comment_interval
    while True:
        try:
            cl.load_settings(SESSION_PATH)
            if cl.user_id:
                media_id = cl.media_id(post_url)
                cl.comment(media_id, comment_text)
                print("✅ Izoh qoldirildi:", comment_text)
            else:
                print("⚠️ Bot login bo‘lmagan!")
        except Exception as e:
            print("❌ Xatolik:", e)
        await asyncio.sleep(comment_interval)

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    if msg.from_user.id != int(ADMIN_ID):
        return await msg.answer("❌ Sizga ruxsat yo‘q!")
    await msg.answer("Salom! Instagram botni boshqarish uchun buyruqlar:\n"
                     "/login - Instagram login\n"
                     "/set_comment - Izoh matni\n"
                     "/set_post - Post URL\n"
                     "/set_interval - Vaqt oraliq\n"
                     "/status - Instagram sessiya statusi")

@dp.message_handler(commands=["login"])
async def login(msg: types.Message):
    login_url = "https://your-koyeb-app.koyeb.app/login"
    await msg.answer(f"Instagramga kirish uchun [Login]({login_url}) tugmasini bosing.", parse_mode="Markdown")

@dp.message_handler(commands=["set_comment"])
async def set_comment(msg: types.Message):
    global comment_text
    comment_text = msg.text.replace("/set_comment ", "")
    await msg.answer(f"✅ Izoh yangilandi: {comment_text}")

@dp.message_handler(commands=["set_post"])
async def set_post(msg: types.Message):
    global post_url
    post_url = msg.text.replace("/set_post ", "")
    await msg.answer(f"✅ Post manzili yangilandi: {post_url}")

@dp.message_handler(commands=["set_interval"])
async def set_interval(msg: types.Message):
    global comment_interval
    comment_interval = int(msg.text.replace("/set_interval ", ""))
    await msg.answer(f"✅ Izoh yozish oraliq vaqti: {comment_interval} sekund")

@dp.message_handler(commands=["status"])
async def session_status(msg: types.Message):
    url = "https://your-koyeb-app.koyeb.app/session_status"
    response = requests.get(url).json()
    await msg.answer(f"{response['message']}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(comment_loop())
    executor.start_polling(dp, skip_updates=True)
