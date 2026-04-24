from telethon import TelegramClient

client = TelegramClient(
    "sessions/session1",
    
api_id,
    "api_hash:"  #обязательно добавить на свое
)   

client.start()   # введёшь номер и код
client.disconnect()

print("✅ session1 успешно создана")
