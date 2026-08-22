import os
import asyncio
import logging
from telethon import TelegramClient, events
from aiohttp import web

logging.basicConfig(level=logging.INFO)

API_ID = int(os.environ.get("API_ID", 38398715))
API_HASH = os.environ.get("API_HASH", "6d70a41fbc67908aad547a31c3cfa9c3a")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8842108955:AAHJyPa7PjCSmOM7HdYbSl3NzdK8ckgdfWE")

bot = TelegramClient('universal_forwarder_bot', API_ID, API_HASH)

FORWARD_MAP = {}
PEER_ENTITIES = {}

def clean_id(chat_id: int) -> int:
    """Telethon ke positive aur negative ID formats ko normalize karta hai"""
    s = str(chat_id)
    if s.startswith("-100"):
        return int(s[4:])
    elif s.startswith("-"):
        return int(s[1:])
    return int(s)

# Command: Ping / Register
@bot.on(events.NewMessage(pattern=r'^/ping'))
async def ping_handler(event):
    chat = await event.get_chat()
    c_id = clean_id(chat.id)
    PEER_ENTITIES[c_id] = chat
    logging.info(f"Registered peer: {c_id}")
    await event.reply(f"Group Registered!\nRaw ID: `{chat.id}`\nClean ID: `{c_id}`")

# Command: Set Forward Route
@bot.on(events.NewMessage(pattern=r'^/setforward\s+(-?\d+)\s+(-?\d+)'))
async def set_forward_handler(event):
    src = clean_id(int(event.pattern_match.group(1)))
    tgt = clean_id(int(event.pattern_match.group(2)))
    
    FORWARD_MAP[src] = tgt
    await event.reply(f"Forward route connected:\n`{src}` ➔ `{tgt}`")

# Command: Active List
@bot.on(events.NewMessage(pattern=r'^/list'))
async def list_routes(event):
    if not FORWARD_MAP:
        await event.reply("Koi route active nahi hai.")
        return
    text = "**Active Routes:**\n"
    for s, t in FORWARD_MAP.items():
        text += f"• `{s}` ➔ `{t}`\n"
    await event.reply(text)

# Auto Forwarder
@bot.on(events.NewMessage())
async def forward_handler(event):
    if event.is_private or event.text.startswith('/'):
        return
    
    chat = await event.get_chat()
    c_id = clean_id(chat.id)
    PEER_ENTITIES[c_id] = chat
    
    if c_id in FORWARD_MAP:
        target_id = FORWARD_MAP[c_id]
        target_entity = PEER_ENTITIES.get(target_id, target_id)
        try:
            await bot.send_message(target_entity, event.message)
            logging.info(f"Forwarded from {c_id} to {target_id}")
        except Exception as e:
            logging.error(f"Failed to forward: {e}")

# Render Web Server
async def handle_ping(request):
    return web.Response(text="Bot active 24/7")

async def start_http_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

async def main():
    await bot.start(bot_token=BOT_TOKEN)
    await start_http_server()
    logging.info("Bot is listening...")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
    
