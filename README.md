# Pokemon Community Game Discord Bot

A Discord bot that monitors Pokemon spawns in Twitch chat and sends them to your Discord server with enhanced information, catch rates, and statistics.

## Features

- 🔍 Automatic Pokemon spawn detection
- ✨ Shiny notifications
- 📊 Detailed spawn statistics
- 🎯 Catch rate calculations
- 🎮 Interactive buttons
- 📈 Spawn history tracking

## Commands

- `/setup #channel` - Set which channel receives Pokemon notifications
- `/lastspawn` - Show the last Pokemon spawn
- `/stats` - Show spawn statistics
- `/shinies` - Show recent shiny spawns
- `/rarest` - Show rarest Pokemon spawns

## Quick Start

1. [Click here to add the bot to your server](https://discord.com/api/oauth2/authorize?client_id=1341192170371285123&permissions=274878221312&scope=bot%20applications.commands)
2. Use `/setup #channel` to choose where Pokemon spawns appear
3. That's it! The bot will now send Pokemon spawns to your channel

## Add Bot to Your Server

1. [Click here to add the bot to your server](YOUR_OAUTH_URL)
2. Use `/setup #channel` to choose where Pokemon notifications appear
3. The bot will now send spawn notifications to your selected channel

Note: The bot is hosted by the community. If you experience downtime, please contact the bot owner.

## Required Permissions

The bot needs these permissions in the channel:
- View Channels
- Send Messages
- Embed Links
- Use External Emojis
- Add Reactions

## Self-Hosting

If you want to host your own instance:

1. Clone this repository
2. Create a `.env` file with your tokens:
```env
# Twitch settings
TWITCH_TOKEN='your_oauth_token'
TWITCH_CHANNEL='your_channel'
TWITCH_MONITOR_CHANNEL='target_channel'

# Discord settings
DISCORD_TOKEN='your_bot_token'
DISCORD_CHANNEL_ID=your_channel_id
```

3. Install Python 3.9+ and required packages:
```bash
pip install -r requirements.txt
```

4. Run the bot:
```bash
python pokemon.py
```

## Ball Types and Catch Rates
| Ball Type | Base Rate | Special Effect |
|-----------|-----------|----------------|
| Poke Ball | 30% | Standard ball |
| Great Ball | 55% | Higher catch rate |
| Ultra Ball | 80% | Best standard ball |
| Premier Ball | 30% | Basic alternative |
| Master Ball | 100% | Guaranteed catch |
| Timer Ball | 10-90% | Time scaling |
| Quick Ball | 10-90% | Early throw bonus |
| Net Ball | 70% | Water/Bug bonus |
| Heavy Ball | 20-80% | Weight scaling |

## Credits
- Pokemon sprites: [Pokemon Showdown](https://play.pokemonshowdown.com)
- Game data: [Pokemon Community Game](https://discord.gg/BvaNvMD)
- Pokemon info: [PokeAPI](https://pokeapi.co)
