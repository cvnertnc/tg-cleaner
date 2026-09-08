# Telegram Message Cleaner

This project deletes messages from Telegram groups and channels using your user account session. It can be run locally via terminal or automatically via GitHub Actions.

---

## Features

- Delete messages from a single chat (group, channel, supergroup)
- Delete your own messages from all groups you are currently a member of
- Two modes: `own` (only your messages) or `all` (everyone's messages)
- Works with both @username and numeric chat IDs (e.g., `-1001234567890`)
- Handles Telegram rate limits (FloodWait) automatically
- Session file stored securely; can be used locally or as a Base64 secret in GitHub Actions

---

## Requirements

- Python 3.7+
- Telethon library
- Telegram API credentials (API ID and API Hash) from [my.telegram.org](https://my.telegram.org)
- A valid Telegram session file (created once)

---

## Local Terminal Usage

### 1. Install Dependencies

```bash
pip install telethon
```

2. Set Environment Variables

You need to export your API credentials:

```bash
export TELEGRAM_API_ID=123456
export TELEGRAM_API_HASH=abcdef123456...
```

3. Create a Session File (First Time Only)

Run the interactive session creator:

```bash
python tg-cleaner.py --create-session
```

You will be prompted for:

· API ID
· API Hash
· Phone number (with country code)
· Session file name (default: my_session)

This will generate a file named my_session.session in the current directory.

4. Run the Script

Delete your own messages from a specific chat

```bash
python tg-cleaner.py -1001644013873 own 500
```

Parameters:

· chat_identifier: @username or numeric ID (use -100... for supergroups)
· mode: own or all (default: own)
· limit: number of recent messages to fetch (default: 1000)

Delete all messages (yours and others) from a channel

```bash
python tg-cleaner.py @my_channel all 2000
```

Delete your own messages from all groups you are a member of

```bash
python tg-cleaner.py --all-groups --mode own --limit 1000
```

View full usage help

```bash
python tg-cleaner.py
```

---

GitHub Actions Usage

You can run the script automatically in the cloud without any local setup.

1. Fork or Clone the Repository

2. Add Secrets to GitHub

Go to Settings → Secrets and variables → Actions and add these secrets:

· TELEGRAM_API_ID – your API ID
· TELEGRAM_API_HASH – your API hash
· TELEGRAM_SESSION_BASE64 – Base64 encoded session file

To generate the Base64 string from your local my_session.session:

```bash
base64 -w0 my_session.session
```

Copy the output and paste it as the secret value.

3. Run the Workflow

Go to the Actions tab, select Telegram Message Cleaner, click Run workflow.

Fill in the inputs:

Input Description Required
action single-chat or all-groups Yes
chat Chat identifier (for single-chat) Yes (if action is single-chat)
mode own or all No (default: own)
limit Number of messages to fetch No (default: 1000)

Click Run workflow to start the deletion process.

---

Environment Variables Reference

Variable Description Required
TELEGRAM_API_ID Telegram API ID Yes
TELEGRAM_API_HASH Telegram API hash Yes
TELEGRAM_SESSION_BASE64 Base64 encoded session file (GitHub Actions only) Yes (for Actions)

Local terminal uses the session file directly (my_session.session) and does not require TELEGRAM_SESSION_BASE64.

---

Important Notes

· Always test with mode: own first to avoid accidentally deleting others' messages.
· The all-groups action scans only groups (basic groups and supergroups), not channels. To delete from channels, use single-chat.
· If you encounter rate limits (FloodWait), the script automatically waits and retries.
· The session file (my_session.session) is sensitive. Never commit it to version control. Use .gitignore to exclude it.
· For GitHub Actions, the session file is decoded from the secret at runtime and never stored in the repository.

---

Local Development Tips

· To test without actually deleting messages, you can run the script with a small limit value (e.g., 10) to verify it finds the correct messages.
· If you want to simulate deletion in dry-run mode, you can modify the script to print instead of delete (not implemented by default, but you can add a DRY_RUN flag locally).
· Use python tg-cleaner.py without arguments to see the full usage help.

---

Troubleshooting

· "No messages found" – The chat identifier may be incorrect, or you may not be a member.
· "FloodWait" – The script handles this automatically by sleeping. Be patient.
· "Cannot access chat" – Ensure you have permission to view messages in that chat.
· Session expired – Recreate the session file using --create-session.
