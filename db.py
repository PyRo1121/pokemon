import asyncio
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional


class PokemonDB:
    def __init__(self, db_path: str = "pokemon_stats.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            # Create tables
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS spawns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pokemon_name TEXT NOT NULL,
                    is_shiny BOOLEAN,
                    tier TEXT,
                    types TEXT,
                    base_stats TEXT,
                    catch_rates TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            c.execute(
                """
                CREATE TABLE IF NOT EXISTS statistics (
                    pokemon_name TEXT PRIMARY KEY,
                    spawn_count INTEGER DEFAULT 1,
                    shiny_count INTEGER DEFAULT 0,
                    last_seen DATETIME,
                    catch_success_rate REAL DEFAULT 0.0
                )
            """
            )

            c.execute(
                """
                CREATE TABLE IF NOT EXISTS commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    command TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            c.execute(
                """
                CREATE TABLE IF NOT EXISTS server_configs (
                    guild_id TEXT PRIMARY KEY,
                    channel_id TEXT NOT NULL,
                    added_by TEXT NOT NULL,
                    added_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.commit()

    async def add_spawn(self, pokemon_data: Dict):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO spawns (
                    pokemon_name, is_shiny, tier, types, base_stats, catch_rates, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    pokemon_data["name"],
                    pokemon_data["is_shiny"],
                    pokemon_data["tier"],
                    pokemon_data["types"],
                    pokemon_data["base_stats"],
                    pokemon_data["catch_rates"],
                    datetime.now(),
                ),
            )

            # Update statistics
            c.execute(
                """
                INSERT INTO statistics (pokemon_name, spawn_count, shiny_count, last_seen)
                VALUES (?, 1, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(pokemon_name) DO UPDATE SET
                spawn_count = spawn_count + 1,
                shiny_count = shiny_count + ?,
                last_seen = CURRENT_TIMESTAMP
            """,
                (
                    pokemon_data["name"],
                    1 if pokemon_data["is_shiny"] else 0,
                    1 if pokemon_data["is_shiny"] else 0,
                ),
            )

            conn.commit()

    async def add_command(self, user_id: str, command: str):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO commands (user_id, command, timestamp)
                VALUES (?, ?, ?)
            """,
                (user_id, command, datetime.now()),
            )
            conn.commit()

    async def get_last_spawn(self) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                """
                SELECT * FROM spawns
                ORDER BY timestamp DESC LIMIT 1
            """
            )
            spawn = c.fetchone()
            if spawn:
                return {
                    "name": spawn[1],
                    "is_shiny": spawn[2],
                    "tier": spawn[3],
                    "types": spawn[4],
                    "base_stats": spawn[5],
                    "catch_rates": spawn[6],
                    "timestamp": spawn[7],
                }
            return None

    async def get_spawn_stats(self) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                """
                SELECT COUNT(*) as total_spawns,
                       SUM(CASE WHEN is_shiny = 1 THEN 1 ELSE 0 END) as total_shinies,
                       COUNT(DISTINCT pokemon_name) as unique_pokemon
                FROM spawns
            """
            )
            return dict(
                zip(["total_spawns", "total_shinies", "unique_pokemon"], c.fetchone())
            )

    async def get_rarest_spawns(self, limit: int = 5) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                """
                SELECT pokemon_name, spawn_count, shiny_count, last_seen
                FROM statistics
                ORDER BY spawn_count ASC
                LIMIT ?
            """,
                (limit,),
            )
            return [
                dict(zip(["name", "count", "shinies", "last_seen"], row))
                for row in c.fetchall()
            ]

    async def get_recent_shinies(self, limit: int = 5) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                """
                SELECT pokemon_name, timestamp, tier, types
                FROM spawns
                WHERE is_shiny = 1
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (limit,),
            )
            return [
                dict(zip(["name", "timestamp", "tier", "types"], row))
                for row in c.fetchall()
            ]

    async def set_server_channel(self, guild_id: str, channel_id: str, user_id: str):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                """
                INSERT OR REPLACE INTO server_configs (guild_id, channel_id, added_by)
                VALUES (?, ?, ?)
            """,
                (guild_id, channel_id, user_id),
            )
            conn.commit()

    async def get_server_channel(self, guild_id: str) -> str:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT channel_id FROM server_configs WHERE guild_id = ?", (guild_id,)
            )
            result = c.fetchone()
            return result[0] if result else None
