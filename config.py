import os
from dotenv import load_dotenv

# Load environment variables from .env file in development
if os.path.exists('.env'):
    load_dotenv()

# Twitch Configuration
TWITCH_TOKEN = os.environ.get('TWITCH_TOKEN')
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')
TWITCH_ACCESS_TOKEN = os.getenv('TWITCH_ACCESS_TOKEN')
TWITCH_REFRESH_TOKEN = os.getenv('TWITCH_REFRESH_TOKEN')
TWITCH_USER_ID = os.getenv('TWITCH_USER_ID')
TWITCH_CHANNEL = os.getenv('TWITCH_CHANNEL')
TWITCH_MONITOR_CHANNEL = os.getenv('TWITCH_MONITOR_CHANNEL')

# Discord Configuration
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID', 0))
DISCORD_CLIENT_ID = int(os.getenv('DISCORD_CLIENT_ID', 0))
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
DISCORD_GUILD_ID = int(os.getenv('DISCORD_GUILD_ID', '0'))

# Simple Bot Invite URL
OAUTH2_URL = f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&permissions=274878221312&scope=bot%20applications.commands"

# Web Application Settings
WEB_HOST = os.getenv('WEB_HOST', 'http://localhost:3000')
TWITCH_REDIRECT_URI = f"{WEB_HOST}/auth/twitch/callback"

# Database for storing user configurations
USER_DB_PATH = "user_configs.db"
