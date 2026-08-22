import os
import asyncio
from telethon import TelegramClient, events
from aiohttp import web

api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("BOT_TOKEN")

MAIN_CHAT = int(os.environ.get("MAIN_CHAT_ID"))
PRIVATE_CHAT = int(os.environ.get("PRIVATE_CHAT_ID"))

bot = TelegramClient('bot', api_id, api_hash)

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

# Render ko live rakhne ke liye fake web server
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

async def main():
    await bot.start(bot_token=bot_token)
    await start_server()
    print("Bot Running Successfully on Render!")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
