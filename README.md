# 🧹 Telegram Message Cleaner

This project automatically deletes **all your own messages** from **Telegram groups you are currently a member of**, using your **user account session** (not a bot).

It runs via **GitHub Actions**, so you can trigger it manually or schedule it to run in the cloud — no local setup required.

---

## ⚙️ Features

- Scans all groups you’re currently a member of  
- Deletes only **your messages**, not others’  
- Handles Telegram FloodWait (rate limits) automatically  
- Supports **dry-run mode** (simulates deletion safely)  
- Works entirely through **GitHub Actions**

---

## 🧩 Environment Variables

| Variable | Description | Required | Example |
|-----------|-------------|-----------|----------|
| `TELEGRAM_API_ID` | Telegram API ID | ✅ | `123456` |
| `TELEGRAM__API_HASH` | Telegram API hash (**double underscore**) | ✅ | `abcdef123456...` |
| `TELEGRAM_SESSION_STRING` | Your Telethon StringSession | ✅ | `1AAgA...` |
| `DRY_RUN` | `1` → simulation only (no deletion) | ❌ | `1` |
| `CHUNK_SIZE` | Number of messages deleted per batch | ❌ | `100` |
| `DELAY_BETWEEN_CHUNKS` | Delay (seconds) between batches | ❌ | `1.0` |

> ⚠️ For the first run, always set `DRY_RUN` to `"1"`.  
> Once you verify it’s working, remove it or set it to `"0"` for real deletion.

---

## 🧰 How to Use

1. Fork or clone this repository.  
2. Add the following **repository secrets** in GitHub:  
   - `TELEGRAM_API_ID`  
   - `TELEGRAM__API_HASH`  
   - `TELEGRAM_SESSION_STRING`  
3. (Optional) Add extra environment variables like `DRY_RUN`, `CHUNK_SIZE`, or `DELAY_BETWEEN_CHUNKS`.  
4. Go to **Actions → Delete Telegram messages → Run workflow** and trigger it manually.

---

## ⚠️ Limitations

- Only works for **groups you are still a member of**.  
- Cannot delete messages from groups you left or were removed from.  
- Cannot access secret chats (Telegram limitation).  
- Very old messages might not be deletable due to Telegram restrictions.

---

## 🧠 Recommended Settings

```yaml
DRY_RUN: "1"
CHUNK_SIZE: "100"
DELAY_BETWEEN_CHUNKS: "1.0"