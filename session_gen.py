import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import SessionPasswordNeeded
from pyrogram.types import Message
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, TELETHON_API_ID, TELETHON_API_HASH

bot = Client("session_generator_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Telethon client setup
telethon_client = TelegramClient(StringSession(), TELETHON_API_ID, TELETHON_API_HASH)

# Function to generate session string using Pyrogram
async def generate_pyrogram_session(client, message: Message):
    await message.reply("Please enter your phone number in international format (e.g., +123456789):")

    phone_number = await bot.listen(message.chat.id)
    phone_number = phone_number.text

    user_client = Client(":memory:", api_id=API_ID, api_hash=API_HASH)

    await user_client.connect()
    
    try:
        code = await user_client.send_code(phone_number)
        await message.reply("Please enter the code you received:")
        
        code_text = await bot.listen(message.chat.id)
        code_text = code_text.text.strip()

        try:
            await user_client.sign_in(phone_number, code_text)
        except SessionPasswordNeeded:
            await message.reply("Please enter your two-step verification password:")
            password = await bot.listen(message.chat.id)
            password = password.text.strip()
            await user_client.check_password(password)

        session_string = await user_client.export_session_string()
        await message.reply(f"Here is your Pyrogram session string:\n\n`{session_string}`")

    except BadMsgNotification as e:
        if e.error_code == 16:
            await asyncio.sleep(1)
            await generate_pyrogram_session(client, message)
        else:
            await message.reply(f"An error occurred: {str(e)}")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")
    finally:
        await user_client.disconnect()

# Function to generate session string using Telethon
async def generate_telethon_session(client, message: Message):
    await message.reply("Please enter your phone number in international format (e.g., +123456789):")

    phone_number = await bot.listen(message.chat.id)
    phone_number = phone_number.text

    await telethon_client.start(phone_number)

    try:
        session_string = telethon_client.session.save()
        await message.reply(f"Here is your Telethon session string:\n\n`{session_string}`")

    except SessionPasswordNeededError:
        await message.reply("Please enter your two-step verification password:")
        password = await bot.listen(message.chat.id)
        password = password.text.strip()
        await telethon_client.start(phone_number, password=password)

        session_string = telethon_client.session.save()
        await message.reply(f"Here is your Telethon session string:\n\n`{session_string}`")

    finally:
        await telethon_client.disconnect()

# Command for owner to check bot statistics
@bot.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats(client, message):
    # Implement your statistics logic here
    # Example: Fetch number of active users, sessions, etc.
    await message.reply("Bot statistics:\nActive users: 100\nSessions: 50")

# Logging bot startup events to a specified channel
@bot.on_chat_member_updated()
async def log_startup(_, member):
    # Replace with your log channel ID
    log_channel_id = -1002105459243  # Example channel ID

    if member.new_chat_member and member.new_chat_member.user.id == bot.get_me().id:
        await bot.send_message(log_channel_id, f"Bot started in {member.chat.title}")

# Start message for users
@bot.on_message(filters.command("start"))
async def start(client, message):
    # Create inline keyboard with buttons for Telethon and Pyrogram
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Generate Pyrogram Session", callback_data="generate_pyrogram"),
            InlineKeyboardButton("Generate Telethon Session", callback_data="generate_telethon")
        ]
    ])

    await message.reply("Welcome to the Session String Generator Bot! Please choose an option:", reply_markup=keyboard)

# Handle inline keyboard button presses
@bot.on_callback_query()
async def callback_handler(client, callback):
    if callback.data == "generate_pyrogram":
        await generate_pyrogram_session(client, callback.message)
    elif callback.data == "generate_telethon":
        await generate_telethon_session(client, callback.message)
    else:
        await callback.answer("Invalid option selected!")

bot.run()
