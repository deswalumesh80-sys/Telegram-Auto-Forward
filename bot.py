import os
import asyncio
import logging
from telethon import TelegramClient, events
from aiohttp import web

logging.basicConfig(level=logging.INFO)

API_ID = int(os.environ.get("API_ID", 38398715))
API_HASH = os.environ.get("API_HASH", "6d70a41fbc67908aad547a31c3cfa9c3a")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8842108955:AAHJyPa7PjCSmOM7HdYbSl3NzdK8ckgdfWE")

GROUP_1 = -1004290323694
GROUP_2 = -1005466448251

bot = TelegramClient('direct_relay_bot', API_ID, API_HASH)

# Group 1 -> Group 2
@bot.on(events.NewMessage(chats=GROUP_1))
async def g1_to_g2(event):
    logging.info(f"Received message in Group 1: {event.message.id}")
    try:
        await bot.send_message(GROUP_2, event.message)
        logging.info("Successfully forwarded to Group 2")
    except Exception as e:
        logging.error(f"Error forwarding to Group 2: {e}")

# Group 2 -> Group 1
@bot.on(events.NewMessage(chats=GROUP_2))
async def g2_to_g1(event):
    logging.info(f"Received message in Group 2: {event.message.id}")
    try:
        await bot.send_message(GROUP_1, event.message)
        logging.info("Successfully forwarded to Group 1")
    except Exception as e:
        logging.error(f"Error forwarding to Group 1: {e}")

async def handle_ping(request):
    return web.Response(text="Bot active 24/7")

async def start_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

async def main():
    await bot.start(bot_token=BOT_TOKEN)
    
    # Force peer cache resolution
    try:
        await bot.get_entity(GROUP_1)
        await bot.get_entity(GROUP_2)
        logging.info("Both groups successfully cached and linked!")
    except Exception as e:
        logging.error(f"Peer resolve error: {e}")
        
    await start_server()
    logging.info("Auto Forwarder is 100% Online and Listening!")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
    
