#!/usr/bin/env python3
"""
delete_telegram_messages.py

- TELEGRAM_API_ID            (required, int)
- TELEGRAM_API_HASH         (required, str)   <- dikkat: çift alt çizgi adını sen verdiğin gibi kullanıyorum
- TELEGRAM_SESSION_STRING    (required, str)   <- Telethon StringSession
Optional env:
- DRY_RUN                    (if "1" -> do not actually delete, just report)
- CHUNK_SIZE                 (default 100)
- DELAY_BETWEEN_CHUNKS       (default 1.0 seconds)
"""

import os
import asyncio
import logging
from telethon import TelegramClient, errors
from telethon.sessions import StringSession
from telethon.tl.types import Channel, Chat

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

async def main():
    # env
    api_id = int(os.environ["TELEGRAM_API_ID"])
    api_hash = os.environ["TELEGRAM_API_HASH"]
    session_str = os.environ["TELEGRAM_SESSION_STRING"]
    DRY_RUN = os.environ.get("DRY_RUN", "0") == "1"
    CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "100"))
    DELAY = float(os.environ.get("DELAY_BETWEEN_CHUNKS", "1.0"))

    client = TelegramClient(StringSession(session_str), api_id, api_hash)
    await client.start()
    me = await client.get_me()
    my_id = me.id
    logging.info(f"Logged in as {getattr(me, 'username', '') or getattr(me,'first_name','<no-name>')} (id={my_id})")
    total_deleted = 0
    total_found = 0

    try:
        async for dialog in client.iter_dialogs():
            entity = dialog.entity

            # treat as "group" if it's a Chat OR a Channel with megagroup=True (supergroup)
            is_group = isinstance(entity, Chat) or (isinstance(entity, Channel) and getattr(entity, "megagroup", False))
            if not is_group:
                continue

            chat_title = getattr(entity, "title", str(entity))
            logging.info(f"Scanning group: {chat_title} (id={getattr(entity,'id', 'unknown')})")

            buffer_ids = []
            found_in_chat = 0

            # iterate only messages from this user
            async for msg in client.iter_messages(entity, from_user=my_id):
                found_in_chat += 1
                buffer_ids.append(msg.id)

                if len(buffer_ids) >= CHUNK_SIZE:
                    total_found += len(buffer_ids)
                    if DRY_RUN:
                        logging.info(f"[DRY_RUN] Would delete {len(buffer_ids)} messages in '{chat_title}'")
                    else:
                        try:
                            await client.delete_messages(entity, buffer_ids)
                            logging.info(f"Deleted {len(buffer_ids)} messages in '{chat_title}'")
                            total_deleted += len(buffer_ids)
                        except errors.FloodWaitError as e:
                            logging.warning(f"FloodWait: sleeping {e.seconds} seconds")
                            await asyncio.sleep(e.seconds + 1)
                            await client.delete_messages(entity, buffer_ids)
                            total_deleted += len(buffer_ids)
                        except Exception as e:
                            logging.exception(f"Failed to delete messages in {chat_title}: {e}")
                    buffer_ids = []
                    await asyncio.sleep(DELAY)

            # leftover
            if buffer_ids:
                total_found += len(buffer_ids)
                if DRY_RUN:
                    logging.info(f"[DRY_RUN] Would delete {len(buffer_ids)} messages in '{chat_title}'")
                else:
                    try:
                        await client.delete_messages(entity, buffer_ids)
                        logging.info(f"Deleted {len(buffer_ids)} messages in '{chat_title}'")
                        total_deleted += len(buffer_ids)
                    except errors.FloodWaitError as e:
                        logging.warning(f"FloodWait: sleeping {e.seconds} seconds")
                        await asyncio.sleep(e.seconds + 1)
                        await client.delete_messages(entity, buffer_ids)
                        total_deleted += len(buffer_ids)
                    except Exception as e:
                        logging.exception(f"Failed to delete messages in {chat_title}: {e}")
                await asyncio.sleep(DELAY)

            if found_in_chat:
                logging.info(f"Finished group: {chat_title} — found {found_in_chat} messages from you.")

    finally:
        logging.info(f"Summary: found {total_found} messages from you in groups. Deleted: {total_deleted}.")
        await client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Aborted by user")