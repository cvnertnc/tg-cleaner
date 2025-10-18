import asyncio
import os
import sys
from telethon import TelegramClient

api_id = int(os.environ.get("TELEGRAM_API_ID"))
api_hash = os.environ.get("TELEGRAM_API_HASH")
session_str = os.environ.get("TELEGRAM_SESSION_STRING")
chat = "@cvnertnc_chat"
delete_mode = "all"
delay_between_deletes = 0.20

async def main():
    client = TelegramClient.from_string(session_str, api_id, api_hash)
    await client.start()

    me = await client.get_me()
    me_id = me.id
    print(f"Logged in as {me.first_name} ({me_id}). Mode: {delete_mode}")

    messages = await client.get_messages(chat, limit=None)

    messages.reverse()

    for message in messages:
        try:
            should_delete = False
            if delete_mode == "own":
                if message.from_id and getattr(message.from_id, "user_id", None) == me_id:
                    should_delete = True
            else:
                should_delete = True

            if not should_delete:
                continue

            await client.delete_messages(chat, message.id)
            print(f"Deleted {message.id}")
            await asyncio.sleep(delay_between_deletes)

        except Exception as e:
            print(f"Could not delete {getattr(message, 'id', 'unknown')}: {e}", file=sys.stderr)

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())