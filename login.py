import asyncio
import os
from telethon import TelegramClient

# ================= ТВОИ ДАННЫЕ =================
API_ID = 23748926  # заполни свой API_ID с https://my.telegram.org
API_HASH = "f933830a116df1bece5ee84cba540b01"  # заполни свой API_HASH
SESSION_NAME = "session1"
# ===============================================

os.makedirs("sessions", exist_ok=True)


async def main():
    if not API_ID or not API_HASH:
        print("❌ Ошибка: заполни API_ID и API_HASH в login.py")
        print("   Получи их на https://my.telegram.org/apps")
        return

    session_path = f"sessions/{SESSION_NAME}"
    client = TelegramClient(session_path, API_ID, API_HASH)

    try:
        await client.connect()
        print("✅ Подключено к Telegram")

        if not await client.is_user_authorized():
            print("📱 Требуется авторизация...")
            await client.start()
        else:
            print("✅ Уже авторизован")

        me = await client.get_me()
        print(f"✅ Успешно! ID: {me.id}, Username: @{me.username or 'нет'}")
        print(f"📁 Сессия сохранена: {session_path}.session")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
