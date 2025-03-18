import asyncio
from instagrapi import Client
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor

# 🔹 Telegram bot ma'lumotlari (FAQAT SHULARNI O‘ZGARTIRING)
TELEGRAM_BOT_TOKEN = "7400009988:AAH8g6s0jvgflZueAzZw4YyvhcN1i44wej8"  # Telegram bot tokenini o‘rnating
ADMIN_ID = 6272205785  # O'zingizning Telegram ID'ingiz

# 🔹 Instagram ma'lumotlari (Bot orqali o‘zgartiriladi)
insta_username = "your_username"
insta_password = "your_password"
post_url = "https://www.instagram.com/p/XXXXXXX/"
comment_text = "Salom! Bu avtomatik izoh 😊"  # Default izoh

# 🔹 Instagram va Telegram bot obyektlari
cl = Client()
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

# 🔹 Bot ishlash flag va interval
running = False
interval = 300  # Default: 5 daqiqa

async def comment_loop():
    """ Instagram'ga avtomatik izoh qoldirish sikli """
    global running
    while running:
        try:
            # Instagram'ga login qilish
            cl.login(insta_username, insta_password)
            media_id = cl.media_id(cl.media_pk_from_url(post_url))

            # Eski izohlarni o‘chirish
            comments = cl.media_comments(media_id)
            for comment in comments:
                if comment.user.username == insta_username:
                    cl.comment_delete(media_id, comment.pk)
                    print("Eski izoh o‘chirildi.")

            # Yangi izoh qoldirish
            cl.media_comment(media_id, comment_text)
            print("Yangi izoh qoldirildi:", comment_text)

            await bot.send_message(ADMIN_ID, f"✅ Yangi izoh qoldirildi: {comment_text}")

        except Exception as e:
            print("Xatolik:", e)
            await bot.send_message(ADMIN_ID, f"❌ Xatolik: {e}")

        await asyncio.sleep(interval)  # Dinamik interval

# 🔹 Telegram bot komandalarini sozlash
@dp.message_handler(commands=["start"])
async def start_command(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "✅ Bot ishga tushdi. Quyidagi komandalar mavjud:\n"
            "/start_instagram - Instagram botni ishga tushirish\n"
            "/stop_instagram - Botni to‘xtatish\n"
            "/status - Bot holatini ko‘rish\n"
            "/set_comment [Yangi izoh] - Izohni o‘zgartirish\n"
            "/set_interval [soniya] - Izoh yuborish oraliq vaqtini o‘zgartirish\n"
            "/set_insta [login] [parol] - Instagram login va parolni o‘zgartirish\n"
            "/set_post [post URL] - Post URL'ni o‘zgartirish"
        )

@dp.message_handler(commands=["start_instagram"])
async def start_instagram(message: Message):
    """ Instagram botni ishga tushirish """
    global running
    if message.from_user.id == ADMIN_ID:
        if not running:
            running = True
            asyncio.create_task(comment_loop())
            await message.answer("✅ Instagram bot ishga tushdi!")
        else:
            await message.answer("⚠️ Bot allaqachon ishlayapti!")

@dp.message_handler(commands=["stop_instagram"])
async def stop_instagram(message: Message):
    """ Instagram botni to‘xtatish """
    global running
    if message.from_user.id == ADMIN_ID:
        running = False
        await message.answer("⛔ Bot to‘xtatildi!")

@dp.message_handler(commands=["status"])
async def status_command(message: Message):
    """ Bot holatini tekshirish """
    if message.from_user.id == ADMIN_ID:
        status = "✅ Ishlayapti" if running else "⛔ To‘xtagan"
        await message.answer(
            f"📌 Bot holati: {status}\n"
            f"💬 Hozirgi izoh: {comment_text}\n"
            f"⏳ Interval: {interval} soniya\n"
            f"📷 Instagram: {insta_username}\n"
            f"🔗 Post URL: {post_url}"
        )

@dp.message_handler(commands=["set_comment"])
async def set_comment(message: Message):
    """ Izoh matnini o‘zgartirish """
    global comment_text
    if message.from_user.id == ADMIN_ID:
        new_comment = message.text.replace("/set_comment ", "").strip()
        if new_comment:
            comment_text = new_comment
            await message.answer(f"✅ Yangi izoh o‘rnatildi: {comment_text}")
        else:
            await message.answer("⚠️ Yangi izoh matnini kiriting: `/set_comment Yangi matn`")

@dp.message_handler(commands=["set_interval"])
async def set_interval(message: Message):
    """ Izoh yozish intervalini o‘zgartirish """
    global interval
    if message.from_user.id == ADMIN_ID:
        try:
            new_interval = int(message.text.replace("/set_interval ", "").strip())
            if new_interval >= 60:
                interval = new_interval
                await message.answer(f"✅ Yangi interval o‘rnatildi: {interval} soniya")
            else:
                await message.answer("⚠️ Minimal interval 60 soniya bo‘lishi kerak!")
        except ValueError:
            await message.answer("⚠️ Iltimos, to‘g‘ri son kiriting: `/set_interval 300`")

@dp.message_handler(commands=["set_insta"])
async def set_insta(message: Message):
    """ Instagram login va parolni o‘zgartirish """
    global insta_username, insta_password
    if message.from_user.id == ADMIN_ID:
        parts = message.text.split()
        if len(parts) == 3:
            insta_username = parts[1]
            insta_password = parts[2]
            await message.answer(f"✅ Instagram ma'lumotlari yangilandi!\n👤 Username: {insta_username}")
        else:
            await message.answer("⚠️ To‘g‘ri formatda kiriting: `/set_insta login parol`")

@dp.message_handler(commands=["set_post"])
async def set_post(message: Message):
    """ Post URL'ni o‘zgartirish """
    global post_url
    if message.from_user.id == ADMIN_ID:
        new_post_url = message.text.replace("/set_post ", "").strip()
        if "instagram.com/p/" in new_post_url:
            post_url = new_post_url
            await message.answer(f"✅ Yangi post URL o‘rnatildi: {post_url}")
        else:
            await message.answer("⚠️ To‘g‘ri Instagram post URL kiriting: `/set_post https://www.instagram.com/p/...`")

# 🔹 Botni ishga tushirish
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
