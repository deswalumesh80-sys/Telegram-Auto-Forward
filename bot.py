import os
from pyrogram import Client, filters

# Environment variables se data utha rahe hain (jo aap Render par set karenge)
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("BOT_TOKEN")
main_chat = int(os.environ.get("MAIN_CHAT_ID"))
private_chat = int(os.environ.get("PRIVATE_CHAT_ID"))

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# 1. Main Channel se message copy karke Private Group mein bhejega
@app.on_message(filters.chat(main_chat))
async def forward_to_private(client, message):
    await message.copy(private_chat)
    print("Main channel se message private group mein bhej diya!")

# 2. Private Group se response (Auto-filter ka) wapas Main Channel mein bhejega
@app.on_message(filters.chat(private_chat))
async def forward_to_channel(client, message):
    # Sirf tabhi bhejega agar message kisi bot (Auto-filter) ne bheja hai
    if message.from_user and message.from_user.is_bot:
        await message.copy(main_chat)
        print("Auto-filter ka response main channel mein bhej diya!")

print("Bot chal gaya hai...")
app.run()
