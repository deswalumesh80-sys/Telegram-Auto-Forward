import os
import asyncio
from telethon import TelegramClient, events
from aiohttp import web

API_ID = int(os.environ.get("API_ID", 38398715))
API_HASH = os.environ.get("API_HASH", "6d70a41fbc67908aad547a31c3cfa9c3a")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8842108955:AAHJyPa7PjCSmOM7HdYbSl3NzdK8ckgdfWE")

bot = TelegramClient('universal_forwarder_bot', API_ID, API_HASH)

FORWARD_MAP = {}
PEER_ENTITIES = {}

# Command: Start / Help
@bot.on(events.NewMessage(pattern=r'^/start'))
async def start_handler(event):
    msg = (
        "**Group-to-Group Auto-Forwarder Bot**\n\n"
        "Forwarding set karne ke liye:\n"
        "1. Bot ko dono Groups me Admin banayein.\n"
        "2. Dono groups me ek baar `/ping` likh kar send karein (taaki bot group pehchan le).\n"
        "3. Phir ye command bhejein:\n"
        "`/setforward <SOURCE_ID> <TARGET_ID>`\n\n"
        "Commands:\n"
        "• `/list` - Active routes dekhne ke liye\n"
        "• `/remove <SOURCE_ID>` - Route hatane ke liye"
    )
    await event.reply(msg)

# Group Cache Ping Command
@bot.on(events.NewMessage(pattern=r'^/ping'))
async def ping_handler(event):
    chat = await event.get_chat()
    PEER_ENTITIES[chat.id] = chat
    await event.reply(f"Group registered successfully! ID: `{chat.id}`")

# Command: Set Forward Route
@bot.on(events.NewMessage(pattern=r'^/setforward\s+(-?\d+)\s+(-?\d+)'))
async def set_forward_handler(event):
    source_id = int(event.pattern_match.group(1))
    target_id = int(event.pattern_match.group(2))
    
    FORWARD_MAP[source_id] = target_id
    await event.reply(f"Forward route active:\n`{source_id}` ➔ `{target_id}`")

# Command: Remove Route
@bot.on(events.NewMessage(pattern=r'^/remove\s+(-?\d+)'))
async def remove_forward_handler(event):
    source_id = int(event.pattern_match.group(1))
    if source_id in FORWARD_MAP:
        del FORWARD_MAP[source_id]
        await event.reply(f"ID `{source_id}` ke liye forwarding band kar di gayi hai.")
    else:
        await event.reply("Ye ID mapping list me nahi hai.")

# Command: List Active Routes
@bot.on(events.NewMessage(pattern=r'^/list'))
async def list_routes(event):
    if not FORWARD_MAP:
        await event.reply("Koi route active nahi hai.")
        return
    text = "**Active Routes:**\n"
    for src, tgt in FORWARD_MAP.items():
        text += f"• `{src}` ➔ `{tgt}`\n"
    await event.reply(text)

# Auto Forwarder (Group Messages & Media)
@bot.on(events.NewMessage())
async def forward_handler(event):
    if event.is_private:
        return
    
    chat = await event.get_chat()
    PEER_ENTITIES[chat.id] = chat
    
    if chat.id in FORWARD_MAP:
        target_id = FORWARD_MAP[chat.id]
        target_entity = PEER_ENTITIES.get(target_id, target_id)
        try:
            await bot.send_message(target_entity, event.message)
        except Exception as e:
            print(f"Forwarding error: {e}")

# Fake Web Server for Render
async def handle_ping(request):
    return web.Response(text="Bot is running active!")

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
    print("Bot Active and Ready!")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
        
