import sqlite3

from config import USER_DB_PATH


def init_user_db():
    with sqlite3.connect(USER_DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS user_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                twitch_channel TEXT UNIQUE,
                discord_guild_id TEXT,
                discord_channel_id TEXT,
                twitch_token TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        conn.commit()


def add_user(twitch_channel, discord_guild_id, discord_channel_id, twitch_token):
    with sqlite3.connect(USER_DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO user_configs
            (twitch_channel, discord_guild_id, discord_channel_id, twitch_token)
            VALUES (?, ?, ?, ?)
        """,
            (twitch_channel, discord_guild_id, discord_channel_id, twitch_token),
        )
        conn.commit()
