#!/usr/bin/env python3
"""
Unified Telegram Message Cleaner

Usage:
  python tg_manager.py --create-session
  python tg_manager.py --all-groups [--mode own|all] [--limit LIMIT]
  python tg_manager.py <chat_identifier> [mode] [limit]

  chat_identifier: @username or numeric ID (e.g., -1001234567890)
  mode: all or own (default: own)
  limit: number of messages to fetch (default: 1000)

Environment variables required:
  TELEGRAM_API_ID
  TELEGRAM_API_HASH

Session file: my_session.session (created with --create-session)
"""

import asyncio
import os
import sys
import logging
from telethon import TelegramClient, errors
from telethon.tl.types import Channel, Chat

# ---------- CONFIG ----------
SESSION_FILE = "my_session"       # uses my_session.session
DEFAULT_MODE = "own"
DEFAULT_LIMIT = 1000
DELAY_BETWEEN_DELETES = 0.20
CHUNK_SIZE = 100                  # for --all-groups mode
DELAY_BETWEEN_CHUNKS = 1.0

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ---------- SESSION CREATION ----------
async def create_session():
    print("Telegram Session File Generator")
    print("=" * 40)
    api_id = int(input("API ID (integer): ").strip())
    api_hash = input("API HASH: ").strip()
    phone = input("Phone number (with country code, e.g. +905xxxxxxxxx): ").strip()
    session_name = input(f"Session file name (default: {SESSION_FILE}): ").strip() or SESSION_FILE

    client = TelegramClient(session_name, api_id, api_hash)
    await client.start(phone=phone)
    me = await client.get_me()
    print(f"Login successful! Name: {me.first_name} (ID: {me.id})")
    print(f"Session file: {session_name}.session")
    await client.disconnect()
    print("Session created successfully.")

# ---------- DELETE IN A SINGLE CHAT ----------
async def delete_messages_in_chat(client, chat, mode, limit):
    me = await client.get_me()
    my_id = me.id
    print(f"Target: {chat} | Mode: {mode} | Limit: {limit}")

    try:
        messages = await client.get_messages(chat, limit=limit)
    except Exception as e:
        print(f"Failed to fetch messages: {e}")
        return 0

    if not messages:
        print("No messages found or unable to access the chat.")
        return 0

    print(f"Fetched {len(messages)} messages. Sorting oldest first.")
    messages.reverse()

    deleted_count = 0
    total = len(messages)
    for idx, message in enumerate(messages, 1):
        try:
            should_delete = False
            if mode == "own":
                if message.from_id and getattr(message.from_id, "user_id", None) == my_id:
                    should_delete = True
            else:  # all
                should_delete = True

            if not should_delete:
                continue

            await client.delete_messages(chat, message.id)
            deleted_count += 1
            print(f"[{idx}/{total}] Deleted message ID: {message.id}")
            await asyncio.sleep(DELAY_BETWEEN_DELETES)

        except Exception as e:
            print(f"[{idx}/{total}] Failed to delete {getattr(message, 'id', 'unknown')}: {e}")

    return deleted_count

# ---------- DELETE MY MESSAGES IN ALL GROUPS ----------
async def delete_my_messages_all_groups(client, mode, limit):
    me = await client.get_me()
    my_id = me.id
    total_deleted = 0
    total_found = 0

    async for dialog in client.iter_dialogs():
        entity = dialog.entity
        is_group = isinstance(entity, Chat) or (isinstance(entity, Channel) and getattr(entity, "megagroup", False))
        if not is_group:
            continue

        chat_title = getattr(entity, "title", str(entity))
        logging.info(f"Scanning group: {chat_title} (id={getattr(entity, 'id', 'unknown')})")

        try:
            messages = await client.get_messages(entity, limit=limit)
        except Exception as e:
            logging.error(f"Failed to fetch messages from {chat_title}: {e}")
            continue

        if not messages:
            continue

        if mode == "own":
            own_messages = [msg for msg in messages if msg.from_id and getattr(msg.from_id, "user_id", None) == my_id]
        else:
            own_messages = messages

        if not own_messages:
            logging.info(f"No messages to delete in {chat_title}")
            continue

        total_found += len(own_messages)

        for i in range(0, len(own_messages), CHUNK_SIZE):
            chunk = own_messages[i:i+CHUNK_SIZE]
            msg_ids = [msg.id for msg in chunk]
            try:
                await client.delete_messages(entity, msg_ids)
                total_deleted += len(msg_ids)
                logging.info(f"Deleted {len(msg_ids)} messages in '{chat_title}'")
                await asyncio.sleep(DELAY_BETWEEN_CHUNKS)
            except errors.FloodWaitError as e:
                logging.warning(f"FloodWait: sleeping {e.seconds} seconds")
                await asyncio.sleep(e.seconds + 1)
                await client.delete_messages(entity, msg_ids)
                total_deleted += len(msg_ids)
            except Exception as e:
                logging.exception(f"Failed to delete messages in {chat_title}: {e}")

    return total_found, total_deleted

# ---------- MAIN ----------
async def main():
    if len(sys.argv) == 1:
        print(__doc__)
        return

    args = sys.argv[1:]

    if args[0] == "--create-session":
        await create_session()
        return

    if args[0] == "--all-groups":
        mode = DEFAULT_MODE
        limit = DEFAULT_LIMIT
        for i, arg in enumerate(args):
            if arg == "--mode" and i+1 < len(args):
                mode = args[i+1]
            if arg == "--limit" and i+1 < len(args):
                try:
                    limit = int(args[i+1])
                except ValueError:
                    pass
        client = TelegramClient(SESSION_FILE, int(os.environ.get("TELEGRAM_API_ID")), os.environ.get("TELEGRAM_API_HASH"))
        await client.start()
        me = await client.get_me()
        logging.info(f"Logged in as {me.first_name} (ID: {me.id})")
        found, deleted = await delete_my_messages_all_groups(client, mode, limit)
        logging.info(f"Summary: found {found} messages, deleted {deleted}.")
        await client.disconnect()
        return

    # Default: single chat deletion
    chat_input = args[0]
    mode = DEFAULT_MODE
    limit = DEFAULT_LIMIT
    if len(args) >= 2:
        mode = args[1]
    if len(args) >= 3:
        try:
            limit = int(args[2])
        except ValueError:
            pass

    try:
        chat = int(chat_input)
    except ValueError:
        chat = chat_input

    client = TelegramClient(SESSION_FILE, int(os.environ.get("TELEGRAM_API_ID")), os.environ.get("TELEGRAM_API_HASH"))
    await client.start()
    me = await client.get_me()
    logging.info(f"Logged in as {me.first_name} (ID: {me.id})")
    deleted = await delete_messages_in_chat(client, chat, mode, limit)
    logging.info(f"Deleted {deleted} messages.")
    await client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Aborted by user")