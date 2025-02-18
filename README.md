# Pokemon Community Game Discord Bot

A Discord bot that monitors Pokemon Community Game on Twitch and tracks Pokemon spawns with enhanced visualization.

## Features

### Real-time Monitoring
- Spawn detection with animated sprites
- Shiny spawn alerts (1/4096 chance)
- Ball effectiveness tracking
- Type-based catch rates

### Advanced Information Display
- **Pokemon Stats:**
  - Generation and Tier info
  - Type effectiveness
  - Base stats (HP, Speed, etc.)
  - Weight-based catch rates

- **Catch Information:**
  - Ball-specific catch rates
  - Special ball bonuses
  - Time-based ball effectiveness
  - Type-specific ball recommendations

### Database Features
- Spawn history tracking
- Shiny encounter logging
- Rarity statistics
- Catch success rates

### Commands
- `/lastspawn` - View most recent spawn
- `/stats` - Show spawn statistics
- `/rarest` - List rarest encounters
- `/shinies` - Show recent shiny spawns

## Setup

1. Install Python 3.9+ and required packages:
```bash
pip install -r requirements.txt
```

2. Configure config.py with:
```python
# Twitch settings
TWITCH_TOKEN = 'your_oauth_token'
TWITCH_CHANNEL = 'your_channel'
TWITCH_MONITOR_CHANNEL = 'target_channel'

# Discord settings
DISCORD_TOKEN = 'your_bot_token'
DISCORD_CHANNEL_ID = your_channel_id
```

3. Run the bot:
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
