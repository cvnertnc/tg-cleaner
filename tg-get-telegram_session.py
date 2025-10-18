import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

async def main():
    print("Generate TELEGRAM_SESSION (Telethon StringSession)")
    api_id = int(input("API ID (integer): ").strip())
    api_hash = input("API HASH: ").strip()
    phone = input("Phone (with country code, e.g. +905xxxxxxxxx): ").strip()

    client = TelegramClient(StringSession(), api_id, api_hash)
    await client.start(phone=phone)
    session_str = client.session.save()
    print("\n--- YOUR TELEGRAM SESSION STRING ---")
    print(session_str)
    print("--- copy this and keep it secret ---\n")

    save = input("Save to .env file? (y/N): ").strip().lower()
    if save == "y":
        with open(".env", "a", encoding="utf-8") as f:
            f.write(f'TELEGRAM_SESSION="{session_str}"\n')
        print("Saved to .env")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
