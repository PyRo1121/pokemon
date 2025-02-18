import asyncio
from pokemon import TwitchBot, DiscordBot
from discord import Intents
from config import *
from dataclasses import dataclass

@dataclass
class MockAuthor:
    name: str

@dataclass
class MockMessage:
    author: MockAuthor
    content: str

class TestDiscordBot(DiscordBot):
    async def run_test_messages(self):
        await self.wait_until_ready()
        print("Bot is ready, testing basic spawn detection...")
        
        # Regular spawn test
        await send_test_message(self, 
            "pokemoncommunitygame",
            "ACTION TwitchLit A wild Gengar appears TwitchLit"
        )
        await asyncio.sleep(2)
        
        await send_test_message(self,
            "pokeinfobot",
            "ACTION Gen: 1 | Tier: A | Ghost Poison | 40.5 KG | 500 BST | Dusk Ball 80%, Ultra Ball 40%"
        )
        
        await asyncio.sleep(10)
        print("Basic test complete!")

async def send_test_message(bot, author, content):
    msg = MockMessage(MockAuthor(author), content)
    print(f"\nTesting message: {content}")
    await bot.twitch_bot.event_message(msg)

if __name__ == "__main__":
    print("Starting test with Discord connection...")
    intents = Intents.all()
    bot = TestDiscordBot(intents=intents)
    
    @bot.event
    async def on_ready():
        await bot.run_test_messages()
    
    try:
        bot.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        print(f"Test error: {e}")
