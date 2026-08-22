import os
import asyncio
from telethon import TelegramClient, events
from aiohttp import web

# Credentials (Render Environment Variables se)
API_ID = int(os.environ.get("API_ID", 38398715))
API_HASH = os.environ.get("API_HASH", "6d70a41fbc67908aad547a31c3cfa9c3a")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8842108955:AAHJyPa7PjCSmOM7HdYbSl3NzdK8ckgdfWE")

bot = TelegramClient('universal_forwarder_bot', API_ID, API_HASH)

# In-memory mapping: {source_chat_id: target_chat_id}
FORWARD_MAP = {}

# Command: Start / Help
@bot.on(events.NewMessage(pattern=r'^/start'))
async def start_handler(event):
    msg = (
        "**Universal Auto-Forwarder Bot**\n\n"
        "Kisi bhi Channel ya Group se forward set karne ke steps:\n"
        "1. Bot ko dono chats (Source & Target) me Admin banayein.\n"
        "2. Niche diye format me command send karein:\n\n"
        "`/setforward <SOURCE_CHAT_ID> <TARGET_CHAT_ID>`\n\n"
        "Example:\n`/setforward -100123456789 -100987654321`\n\n"
        "Active mappings dekhne ke liye: `/list`\n"
        "Mapping hatane ke liye: `/remove <SOURCE_CHAT_ID>`"
    )
    await event.reply(msg)

# Command: Set Forward Route
@bot.on(events.NewMessage(pattern=r'^/setforward\s+(-?\d+)\s+(-?\d+)'))
async def set_forward_handler(event):
    source_id = int(event.pattern_match.group(1))
    target_id = int(event.pattern_match.group(2))
    
    FORWARD_MAP[source_id] = target_id
    await event.reply(f"Route set ho gaya:\nSource: `{source_id}` -> Target: `{target_id}`")

# Command: Remove Route
@bot.on(events.NewMessage(pattern=r'^/remove\s+(-?\d+)'))
async def remove_forward_handler(event):
    source_id = int(event.pattern_match.group(1))
    if source_id in FORWARD_MAP:
        del FORWARD_MAP[source_id]
        await event.reply(f"Chat ID `{source_id}` ke liye forwarding band kar di gayi hai.")
    else:
        await event.reply("Ye ID mapping list me nahi hai.")

# Command: List Active Mappings
@bot.on(events.NewMessage(pattern=r'^/list'))
async def list_routes(event):
    if not FORWARD_MAP:
        await event.reply("Abhi koi forward route active nahi hai.")
        return
    text = "**Active Routes:**\n"
    for src, tgt in FORWARD_MAP.items():
        text += f"• `{src}` ➔ `{tgt}`\n"
    await event.reply(text)

# Global Message Listener (Messaages & Files forward karega)
@bot.on(events.NewMessage())
async def universal_relay(event):
    if event.is_private:
        return  # Command chats ignore hongi
    
    chat_id = event.chat_id
    if chat_id in FORWARD_MAP:
        target_id = FORWARD_MAP[chat_id]
        try:
            # Pura message, files, media, buttons forward/copy karega
            await bot.send_message(target_id, event.message)
        except Exception as e:
            print(f"Forward error from {chat_id} to {target_id}: {e}")

# Render Web Service ke liye fake HTTP Server (Crash protection)
async def handle_ping(request):
    return web.Response(text="Bot is running active 24/7!")

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
    print("Universal Forwarder Bot Active!")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
    
