import os
import asyncio
from telethon import TelegramClient, events
from aiohttp import web

# Sirf aur sirf Render ke Environment Variables se values aayengi
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH").strip()
BOT_TOKEN = os.environ.get("BOT_TOKEN").strip()

bot = TelegramClient('universal_forwarder_bot', API_ID, API_HASH)

FORWARD_MAP = {}

# Command: Start / Help
@bot.on(events.NewMessage(pattern=r'^/start'))
async def start_handler(event):
    msg = (
        "**Universal Auto-Forwarder Bot**\n\n"
        "Forward set karne ke steps:\n"
        "1. Bot ko Source aur Target dono chats me Admin banayein.\n"
        "2. Ye command send karein:\n\n"
        "`/setforward <SOURCE_CHAT_ID> <TARGET_CHAT_ID>`\n\n"
        "Active routes: `/list`\n"
        "Route remove: `/remove <SOURCE_CHAT_ID>`"
    )
    await event.reply(msg)

# Command: Set Forward Route
@bot.on(events.NewMessage(pattern=r'^/setforward\s+(-?\d+)\s+(-?\d+)'))
async def set_forward_handler(event):
    source_id = int(event.pattern_match.group(1))
    target_id = int(event.pattern_match.group(2))
    
    FORWARD_MAP[source_id] = target_id
    await event.reply(f"Route set ho gaya:\n`{source_id}` ➔ `{target_id}`")

# Command: Remove Route
@bot.on(events.NewMessage(pattern=r'^/remove\s+(-?\d+)'))
async def remove_forward_handler(event):
    source_id = int(event.pattern_match.group(1))
    if source_id in FORWARD_MAP:
        del FORWARD_MAP[source_id]
        await event.reply(f"Chat ID `{source_id}` ke liye forwarding band ho gayi.")
    else:
        await event.reply("Ye ID active list me nahi hai.")

# Command: List Active Mappings
@bot.on(events.NewMessage(pattern=r'^/list'))
async def list_routes(event):
    if not FORWARD_MAP:
        await event.reply("Koi route active nahi hai.")
        return
    text = "**Active Routes:**\n"
    for src, tgt in FORWARD_MAP.items():
        text += f"• `{src}` ➔ `{tgt}`\n"
    await event.reply(text)

# Message & Media Forwarder
@bot.on(events.NewMessage())
async def universal_relay(event):
    if event.is_private:
        return
    
    chat_id = event.chat_id
    if chat_id in FORWARD_MAP:
        target_id = FORWARD_MAP[chat_id]
        try:
            await bot.send_message(target_id, event.message)
        except Exception as e:
            print(f"Forwarding error: {e}")

# Fake Web Server for Render
async def handle_ping(request):
    return web.Response(text="Bot is running!")

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
    print("Bot Successfully Connected & Running!")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
    
