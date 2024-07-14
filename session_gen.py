import asyncio
import logging
from pyrogram import Client
import ntplib
from time import ctime

def sync_time():
    try:
        client = ntplib.NTPClient()
        response = client.request('pool.ntp.org')
        current_time = ctime(response.tx_time)
        print(f"Current system time before sync: {current_time}")
    except Exception as e:
        print(f"Failed to sync time: {e}")

# Call sync_time before starting your bot
sync_time
()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_ID = "21048424"
API_HASH = "1ad8c57a3e3906ee82f5ccbc9aeffb4a"
PHONE_NUMBER = "+917003729439"

async def main():
    # Sync time without sudo
    try:
        current_time = await asyncio.create_subprocess_exec("date")
        await current_time.communicate()
    except Exception as e:
        logger.error(f"Failed to sync time: {e}")
    
    async with Client("my_account", api_id=API_ID, api_hash=API_HASH) as app:
        await app.send_message("me", "Bot started successfully!")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
