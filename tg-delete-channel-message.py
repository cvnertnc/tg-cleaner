import asyncio
import os
from telethon import TelegramClient

api_id = int(os.environ["TELEGRAM_API_ID"])
api_hash = os.environ["TELEGRAM_API_HASH"]
session_str = os.environ["TELEGRAM_SESSION_STRING"]

channel = "cvnertnc"

async def main():
    client = TelegramClient.from_string(session_str, api_id, api_hash)
    await client.start()

    messages = await client.get_messages(channel, limit=None)

    if messages:
        await client.delete_messages(channel, messages)
        print(f"{len(messages)} message deleted.")
    else:
        print("No messages found to delete.")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())