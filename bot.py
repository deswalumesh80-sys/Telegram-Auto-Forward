import os
from telethon import TelegramClient, events

api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("BOT_TOKEN")

MAIN_CHAT = int(os.environ.get("MAIN_CHAT_ID"))
PRIVATE_CHAT = int(os.environ.get("PRIVATE_CHAT_ID"))

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# 1. Main Channel se message sidhe Private Group me
@bot.on(events.NewMessage(chats=MAIN_CHAT))
async def main_to_pri(event):
    if not event.message.sender or not event.message.sender.bot:
        await bot.send_message(PRIVATE_CHAT, event.message)

# 2. Private Group se Auto-filter ka reply wapas Main Channel me
@bot.on(events.NewMessage(chats=PRIVATE_CHAT))
async def pri_to_main(event):
    if event.message.sender and event.message.sender.bot:
        await bot.send_message(MAIN_CHAT, event.message)

print("Bot Running Successfully!")
bot.run_until_disconnected()
