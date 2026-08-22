import os
import asyncio
import logging
from pyrogram import Client, filters

logging.basicConfig(level=logging.INFO)

# Render ke Environment Variables se values fetch hongi
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

MAIN_CHAT_ID = int(os.environ.get("MAIN_CHAT_ID", 0))
PRIVATE_CHAT_ID = int(os.environ.get("PRIVATE_CHAT_ID", 0))

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
        logging.info("Bot successfully started and running on Render!")
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
    
