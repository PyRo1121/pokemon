import asyncio
from pokemon import TwitchBot, DiscordBot
from discord import Intents
from config import *
from dataclasses import dataclass
import datetime

def check_config():
    """Verify all required config values are present"""
    required = [
        'DISCORD_BOT_TOKEN',
        'DISCORD_CHANNEL_ID',
        'TWITCH_TOKEN',
        'TWITCH_CHANNEL',
        'TWITCH_MONITOR_CHANNEL'
    ]
    
    missing = [key for key in required if not globals().get(key)]
    if missing:
        raise ValueError(f"Missing required config values: {', '.join(missing)}")

@dataclass
class MockAuthor:
    name: str

@dataclass
class MockMessage:
    author: MockAuthor
    content: str

async def send_test_message(bot, author, content):
    msg = MockMessage(MockAuthor(author), content)
    print(f"Sending: {content}")
    await bot.twitch_bot.event_message(msg)
    await asyncio.sleep(2)

class TestDiscordBot(DiscordBot):
    async def run_test_sequence(self):
        await self.wait_until_ready()
        print("Bot is ready, starting enhanced test sequence...\n")
        
        # Test Case 1: Legendary Pokemon with all features
        print("\nTest Case 1: Legendary Pokemon with Enhanced Info")
        await send_test_message(self, 
            "pokemoncommunitygame",
            "ACTION ⭐⭐⭐ A wild Mewtwo appears! ⭐⭐⭐"
        )
        await send_test_message(self,
            "pokeinfobot",
            "ACTION Gen: 1 | Tier: S+ | Psychic | 122.0 KG | 680 BST | HP: 106 | Speed: 130 | Master Ball 100%, Ultra Ball 5%"
        )
        await send_test_message(self,
            "pokeinfobot",
            "Database Stats: Spawn Rate: 0.01% | Last Seen: 14 days ago | Catch Success: 12%"
        )
        
        await asyncio.sleep(5)
        
        # Test Case 2: Special Ball Effectiveness
        print("\nTest Case 2: Special Ball Effectiveness")
        await send_test_message(self,
            "pokemoncommunitygame",
            "ACTION A wild Gyarados appears!"
        )
        await send_test_message(self,
            "pokeinfobot",
            "ACTION Gen: 1 | Tier: A | Water Flying | 235.0 KG | 540 BST | HP: 95 | Speed: 81"
        )
        await send_test_message(self,
            "pokeinfobot",
            "Ball Effectiveness: Net Ball 80% (Type Bonus), Heavy Ball 75% (Weight Bonus), Timer Ball 40-90% (Time Scaling)"
        )
        
        await asyncio.sleep(5)
        
        # Test Case 3: Evolution and Status Info
        print("\nTest Case 3: Evolution and Status Info")
        await send_test_message(self,
            "pokemoncommunitygame",
            "ACTION A wild Charmeleon appears!"
        )
        await send_test_message(self,
            "pokeinfobot",
            "ACTION Gen: 1 | Tier: B | Fire | 19.0 KG | 405 BST | HP: 58 | Speed: 80"
        )
        await send_test_message(self,
            "pokeinfobot",
            "Evolution: Charmander (Lv.16) → Charmeleon → Charizard (Lv.36) | Requires: None"
        )
        
        print("\nTest sequence complete! Check Discord for enhanced displays.")

def main():
    print("Starting enhanced Pokemon bot test...")
    try:
        # Verify config before starting
        check_config()
        print(f"Config loaded - Testing with channel: {TWITCH_MONITOR_CHANNEL}")
        
        bot = TestDiscordBot()
        
        @bot.event
        async def on_ready():
            await bot.run_test_sequence()
        
        bot.run(DISCORD_BOT_TOKEN)
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Test error: {e}")

if __name__ == "__main__":
    main()
