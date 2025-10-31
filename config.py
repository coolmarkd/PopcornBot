"""Configuration management for PopcornBot."""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot token from environment variable
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError(
        "DISCORD_BOT_TOKEN environment variable is required. "
        "Please set it in your .env file or environment."
    )

# Validate token format (Discord bot tokens are typically long strings)
# Basic validation: check if it's a reasonable length and not just whitespace
BOT_TOKEN = BOT_TOKEN.strip()
if len(BOT_TOKEN) < 20:  # Discord tokens are much longer, but this is a basic check
    raise ValueError(
        "DISCORD_BOT_TOKEN appears to be invalid or too short. "
        "Please verify your bot token in the .env file."
    )

# Client ID from environment variable (optional but recommended)
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")

# Role names for permissions
GM_ROLE_NAME = "GM"
POPCORN_MANAGER_ROLE_NAME = "Popcorn Manager"

