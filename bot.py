import asyncio
import logging
from pyrogram import Client, filters

logging.basicConfig(level=logging.INFO)

# Hardcoded Credentials
API_ID = 38398715
API_HASH = "6d70a41fbc67908aad547a31c3cfa9c3a"
BOT_TOKEN = "8842108955:AAHJyPa7PjCSmOM7HdYbSl3NzdK8ckgdfWE"

# Chat IDs
MAIN_CHAT_ID = -1004352725251
PRIVATE_CHAT_ID = -1004290323694

app = Client(
    "auto_relay_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# 1. Main Channel se query receive karke Private Group me bhejega
@app.on_message(filters.chat(MAIN_CHAT_ID) & ~filters.bot)
async def forward_to_private(client, message):
    try:
        await message.copy(chat_id=PRIVATE_CHAT_ID)
        logging.info("Query forwarded to Private Group.")
    except Exception as e:
        logging.error(f"Error forwarding to private: {e}")

# 2. Private Group se Auto Filter bot ka response wapas Main Channel me bhejega
@app.on_message(filters.chat(PRIVATE_CHAT_ID))
async def forward_to_main(client, message):
    try:
        if message.from_user and message.from_user.is_bot:
            await message.copy(chat_id=MAIN_CHAT_ID)
            logging.info("Response sent back to Main Chat.")
    except Exception as e:
        logging.error(f"Error forwarding to main: {e}")

async def main():
    async with app:
        logging.info("Bot is active and running...")
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
    
