import discord
import asyncio
from twitchio.ext import commands as tcommands
import webbrowser
import requests
from config import *
from discord import Activity, ActivityType, app_commands
from discord.ui import Button, View
from themes import ThemeManager
from db import PokemonDB

def check_bot_authorized():
    oauth_url = OAUTH2_URL
    print("Bot Authorization URL:")
    print(oauth_url)
    print("\nChecking if bot needs authorization...")
    # Check if bot is in server by making a test API call
    headers = {'Authorization': f'Bot {DISCORD_BOT_TOKEN}'}
    response = requests.get(f'https://discord.com/api/v10/guilds/{DISCORD_GUILD_ID}/members', headers=headers)
    
    if response.status_code != 200:
        print("Bot needs to be authorized. Opening browser...")
        webbrowser.open(oauth_url)
        input("Press Enter after authorizing the bot...")
    else:
        print("Bot is already authorized")

async def verify_discord_permissions():
    """Verify and print Discord bot permissions"""
    auth_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={DISCORD_CLIENT_ID}"
        f"&permissions=534723950656"  # Updated permissions including View Channels and Send Messages
        f"&scope=bot%20applications.commands"
    )
    
    print("\nDiscord Bot Setup:")
    print(f"1. Use this URL to add bot to your server:\n{auth_url}")
    print("\n2. Ensure bot has these permissions in the channel:")
    print("   - View Channels")
    print("   - Send Messages")
    print("   - Create Public Threads")
    print("   - Send Messages in Threads")
    print("   - Embed Links")
    print("   - Attach Files")
    print("   - Read Message History")
    print(f"\n3. Check channel ID: {DISCORD_CHANNEL_ID}")
    return auth_url

class TwitchBot(tcommands.Bot):
    TIER_COLORS = {
        'S': 0xFF0000,  # Red
        'A': 0xFF6B00,  # Orange
        'B': 0x2ECC71,  # Green
        'C': 0x3498DB,  # Blue
        'D': 0x95A5A6   # Gray
    }
    
    TYPE_EMOJIS = {
        'normal': '⚪', 'fire': '🔥', 'water': '💧', 'electric': '⚡',
        'grass': '🌿', 'ice': '❄️', 'fighting': '👊', 'poison': '☠️',
        'ground': '🌍', 'flying': '🦅', 'psychic': '🔮', 'bug': '🐛',
        'rock': '🪨', 'ghost': '👻', 'dragon': '🐉', 'dark': '🌑',
        'steel': '⚙️', 'fairy': '✨'
    }

    def __init__(self):
        super().__init__(
            token=TWITCH_TOKEN.replace('oauth:', ''),
            nick=TWITCH_CHANNEL,  # Use your channel name
            prefix='!',
            initial_channels=[TWITCH_MONITOR_CHANNEL]  # Channel to watch for Pokemon
        )
        self.last_pokemon = None
        self.last_pcg_message = None  # Pokemon Community Game message
        self.last_pib_message = None  # PokeInfoBot message
        self.combined_info = None
        self.session = requests.Session()  # Add session for API calls
        self.last_extra_info = None  # Add storage for extra info
        self.last_evolution_info = None  # Add storage for evolution info
        self.db = PokemonDB()  # Initialize database
    
    async def event_ready(self):
        print(f'Connected to Twitch as {TWITCH_CHANNEL} | Monitoring: {TWITCH_MONITOR_CHANNEL}')

    async def event_message(self, message):
        try:
            author_name = message.author.name.lower() if message.author else "unknown"
            content = message.content
            print(f"Twitch message from {author_name}: {content}")
            
            # Ignore step messages
            if 'step' in content.lower():
                print("Ignoring step-related message")
                return

            # Handle ACTION messages and clean content
            if content.startswith('ACTION'):
                content = content.replace('ACTION', '').strip()
            
            # Clean up any unwanted characters
            content = content.replace('\x01', '').strip()
            
            # Check for Pokemon spawn message
            if author_name == 'pokemoncommunitygame' and 'wild' in content.lower():
                try:
                    # Check if it's a shiny spawn
                    is_shiny = '✨shiny✨' in content.lower()
                    # Extract Pokemon name between "wild" and "appears"
                    pokemon_name = content.split('wild')[1].split('appears')[0].strip()
                    print(f"Pokemon spawn detected: {pokemon_name} {'(SHINY!)' if is_shiny else ''}")
                    self.last_pcg_message = f"Pokemon: {pokemon_name}|Shiny: {is_shiny}"
                    await self.combine_pokemon_info()
                except Exception as e:
                    print(f"Error parsing Pokemon name: {e}")
            
            # Check for PokeInfoBot stats
            elif author_name == 'pokeinfobot':
                if 'Gen:' in content:
                    self.last_pib_message = content
                elif 'Database Stats:' in content:
                    self.last_extra_info = content
                elif 'Evolution:' in content:
                    self.last_evolution_info = content
                elif 'Ball Effectiveness:' in content:
                    self.last_extra_info = content
                await self.combine_pokemon_info()
            
            # Track commands
            elif content.startswith('!'):
                await self.db.add_command(author_name, content)
                
        except Exception as e:
            print(f"Error processing message: {e}")
    
    async def get_pokemon_image(self, pokemon_name):
        try:
            clean_name = pokemon_name.lower().split('-')[0].strip()
            
            # Try Pokemon Showdown animated sprite first
            animated_url = f"https://play.pokemonshowdown.com/sprites/ani/{clean_name}.gif"
            response = self.session.get(animated_url)
            if response.status_code == 200:
                return animated_url
                
            # Try shiny animated sprite
            shiny_animated_url = f"https://play.pokemonshowdown.com/sprites/ani-shiny/{clean_name}.gif"
            response = self.session.get(shiny_animated_url)
            if response.status_code == 200:
                return shiny_animated_url
            
            # Fallback to PokeAPI if no animated sprite found
            response = self.session.get(f"https://pokeapi.co/api/v2/pokemon/{clean_name}")
            if response.status_code == 200:
                data = response.json()
                sprite_options = [
                    data['sprites']['other']['official-artwork']['front_default'],
                    data['sprites']['other']['home']['front_default'],
                    data['sprites']['front_default']
                ]
                for sprite in sprite_options:
                    if sprite:
                        return sprite
            return None
        except Exception as e:
            print(f"Error getting Pokemon image: {e}")
            return None

    def calculate_catch_probability(self, ball_text):
        # Extract percentage from text like "Quick Ball 80%"
        try:
            return int(ball_text.split()[-1].replace('%', ''))
        except:
            return 0

    async def combine_pokemon_info(self):
        if self.last_pcg_message and self.last_pib_message:
            try:
                # Extract Pokemon name and shiny status
                pokemon_info = dict(item.split(": ") for item in self.last_pcg_message.split("|"))
                pokemon_name = pokemon_info['Pokemon'].strip()
                is_shiny = pokemon_info.get('Shiny', 'False') == 'True'
                
                # Parse PIB message for stats
                pib_parts = [part.strip() for part in self.last_pib_message.split('|')]
                stats = {}
                
                for part in pib_parts:
                    if 'Gen:' in part:
                        stats['gen'] = part.replace('Gen:', '').strip()
                    elif 'Tier:' in part:
                        stats['tier'] = part.replace('Tier:', '').strip()
                    elif 'KG' in part:
                        stats['weight'] = part.strip()
                    elif 'BST' in part:
                        stats['bst'] = part.replace('BST:', '').strip()
                
                # Get types (usually the third element after gen and tier)
                if len(pib_parts) > 2:
                    stats['types'] = pib_parts[2].strip()
                
                # Get ball info (usually the last elements)
                stats['balls'] = [p.strip() for p in pib_parts if 'Ball' in p]

                # Get Pokemon image URL
                image_url = await self.get_pokemon_image(pokemon_name)
                
                # Determine embed color based on tier
                tier = stats.get('tier', 'C').upper()
                embed_color = self.TIER_COLORS.get(tier, 0x2ECC71)
                
                # Create embed
                embed = discord.Embed(
                    title=f"✨ {pokemon_name} ✨",
                    color=embed_color
                )
                
                if image_url:
                    embed.set_thumbnail(url=image_url)

                # Add types with emojis
                types = stats.get('types', '').lower().split()
                type_text = ' '.join(f"{self.TYPE_EMOJIS.get(t, '')} {t.title()}" for t in types)

                # Main stats field with emojis
                embed.add_field(
                    name="📊 Basic Info",
                    value=(
                        f"**Generation:** {stats.get('gen', 'Unknown')}\n"
                        f"**Tier:** {tier} {'🏆' if tier in ['S', 'A'] else ''}\n"
                        f"**Type:** {type_text}\n"
                        f"**Weight:** {stats.get('weight', 'Unknown')}\n"
                        f"**Base Stats Total:** {stats.get('bst', 'Unknown')}"
                    ),
                    inline=False
                )

                # Enhanced catch rate field with probabilities
                catch_text = ""  # Initialize catch_text
                if stats.get('balls'):  # Use .get() to avoid KeyError
                    best_ball = max(stats['balls'], key=self.calculate_catch_probability)
                    best_prob = self.calculate_catch_probability(best_ball)
                    
                    catch_text = '\n'.join(
                        f"🎯 {ball.strip()} {'⭐' if self.calculate_catch_probability(ball) == best_prob else ''}"
                        for ball in stats['balls']
                    )
                    
                    embed.add_field(
                        name="📦 Catch Rates",
                        value=catch_text,
                        inline=False
                    )

                # Add evolution info if available
                if self.last_evolution_info:
                    evo_info = self.last_evolution_info.replace('Evolution:', '').strip()
                    embed.add_field(
                        name="⚡ Evolution Chain",
                        value=evo_info,
                        inline=False
                    )

                # Add extra info if available
                if self.last_extra_info:
                    if 'Database Stats:' in self.last_extra_info:
                        stats = self.last_extra_info.replace('Database Stats:', '').strip()
                        embed.add_field(
                            name="📈 Spawn Statistics",
                            value=stats,
                            inline=False
                        )
                    elif 'Ball Effectiveness:' in self.last_extra_info:
                        balls = self.last_extra_info.replace('Ball Effectiveness:', '').strip()
                        embed.add_field(
                            name="🎯 Enhanced Catch Rates",
                            value=balls,
                            inline=False
                        )

                # Add HP and Speed if available
                hp_speed = []
                for part in pib_parts:
                    if 'HP:' in part:
                        hp_speed.append(f"**HP:** {part.split(':')[1].strip()}")
                    elif 'Speed:' in part:
                        hp_speed.append(f"**Speed:** {part.split(':')[1].strip()}")
                if hp_speed:
                    embed.add_field(
                        name="💪 Key Stats",
                        value='\n'.join(hp_speed),
                        inline=True
                    )

                # Footer with timestamp and shiny chance
                footer_text = "✨ 1/4096 chance of being Shiny!"
                if is_shiny:
                    footer_text = "💫 SHINY POKEMON! (1/4096 chance) 💫"
                embed.set_footer(text=footer_text)
                embed.timestamp = discord.utils.utcnow()
                
                self.combined_info = embed
                print(f"Successfully created enhanced embed for {pokemon_name}")
                
                # Clear individual messages
                self.last_pcg_message = None
                self.last_pib_message = None
                self.last_extra_info = None
                self.last_evolution_info = None
                
                # Add spawn to database with safe catch_text
                await self.db.add_spawn({
                    'name': pokemon_name,
                    'is_shiny': is_shiny,
                    'tier': stats.get('tier', 'Unknown'),
                    'types': type_text,
                    'base_stats': f"HP: {stats.get('hp', 'Unknown')}, Speed: {stats.get('speed', 'Unknown')}",
                    'catch_rates': catch_text or "No catch rates available"
                })
                
            except Exception as e:
                print(f"Error creating embed: {e}")
                print(f"PCG message: {self.last_pcg_message}")
                print(f"PIB message: {self.last_pib_message}")
                print(f"Extra info: {self.last_extra_info}")
                print(f"Evolution info: {self.last_evolution_info}")
                self.combined_info = None

class PokemonView(View):
    def __init__(self, bot):
        super().__init__(timeout=60)
        self.bot = bot
        self.add_item(Button(label="📊 Stats", custom_id="stats", style=discord.ButtonStyle.primary))
        self.add_item(Button(label="✨ Shinies", custom_id="shinies", style=discord.ButtonStyle.success))
        self.add_item(Button(label="🏆 Rarest", custom_id="rarest", style=discord.ButtonStyle.danger))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        try:
            if interaction.data["custom_id"] == "stats":
                await self.bot.stats(interaction)
            elif interaction.data["custom_id"] == "shinies":
                await self.bot.shinies(interaction)
            elif interaction.data["custom_id"] == "rarest":
                await self.bot.rarest(interaction)
            return True
        except Exception as e:
            print(f"Button interaction error: {e}")
            return False

class DiscordBot(discord.Client):
    def __init__(self, *args, **kwargs):
        # Set up intents properly
        intents = discord.Intents.default()
        intents.message_content = True  # For reading message content
        intents.members = True          # For member-related features
        intents.presences = True        # For presence updates
        super().__init__(intents=intents, *args, **kwargs)
        self.tree = app_commands.CommandTree(self)
        self.twitch_bot = None
        self.db = PokemonDB()
        self.theme_manager = ThemeManager()
        self.auth_url = None
        
        # Register commands
        @self.tree.command(name="lastspawn", description="Show the last Pokemon spawn")
        async def lastspawn(interaction: discord.Interaction):
            await self.lastspawn(interaction)

        @self.tree.command(name="stats", description="Show Pokemon spawn statistics")
        async def stats(interaction: discord.Interaction):
            await self.stats(interaction)

        @self.tree.command(name="rarest", description="Show rarest Pokemon spawns")
        async def rarest(interaction: discord.Interaction):
            await self.rarest(interaction)

        @self.tree.command(name="shinies", description="Show recent shiny spawns")
        async def shinies(interaction: discord.Interaction):
            await self.shinies(interaction)

        @self.tree.command(name="sync", description="Force sync slash commands (Admin only)")
        async def sync(interaction: discord.Interaction):
            if interaction.user.guild_permissions.administrator:
                try:
                    await self.tree.sync()
                    await interaction.response.send_message("Commands synced!", ephemeral=True)
                except Exception as e:
                    await interaction.response.send_message(f"Sync failed: {e}", ephemeral=True)
            else:
                await interaction.response.send_message("You need admin permissions to sync commands!", ephemeral=True)

        @self.tree.command(
            name="setup",
            description="Set the channel for Pokemon spawn notifications"
        )
        async def setup(interaction: discord.Interaction, channel: discord.TextChannel = None):
            if not interaction.user.guild_permissions.manage_channels:
                await interaction.response.send_message(
                    "❌ You need 'Manage Channels' permission to use this command.",
                    ephemeral=True
                )
                return

            # Use mentioned channel or current channel
            target_channel = channel or interaction.channel
            
            try:
                # Check if bot has permissions in the channel
                perms = target_channel.permissions_for(interaction.guild.me)
                if not all([perms.send_messages, perms.embed_links]):
                    await interaction.response.send_message(
                        f"❌ I need permission to send messages and embeds in {target_channel.mention}",
                        ephemeral=True
                    )
                    return

                # Save channel configuration
                await self.db.set_server_channel(
                    str(interaction.guild_id),
                    str(target_channel.id),
                    str(interaction.user.id)
                )

                await interaction.response.send_message(
                    f"✅ Successfully set {target_channel.mention} as the Pokemon notification channel!",
                    ephemeral=True
                )
                
                # Send test message
                embed = discord.Embed(
                    title="Pokemon Bot Setup Complete!",
                    description="You'll receive Pokemon spawn notifications in this channel.",
                    color=0x2ECC71
                )
                embed.add_field(
                    name="Available Commands",
                    value="`/lastspawn` - Show last spawn\n"
                          "`/stats` - Show statistics\n"
                          "`/shinies` - Show recent shinies\n"
                          "`/rarest` - Show rarest spawns"
                )
                await target_channel.send(embed=embed)

            except Exception as e:
                await interaction.response.send_message(
                    f"❌ Error setting up channel: {str(e)}",
                    ephemeral=True
                )

    async def setup_hook(self):
        try:
            self.auth_url = await verify_discord_permissions()
            self.twitch_bot = TwitchBot()
            self.bg_task = self.loop.create_task(self.post_pokemon_info())
            # Sync commands globally
            await self.tree.sync()
            print("Slash commands synced globally")
        except Exception as e:
            print(f"Failed to initialize: {e}")

    async def on_ready(self):
        print(f'Discord Bot logged in as {self.user} (ID: {DISCORD_CLIENT_ID})')
        try:
            # Set presence first
            await self.change_presence(
                activity=Activity(
                    type=ActivityType.watching,
                    name=f"{TWITCH_MONITOR_CHANNEL}'s Pokémon"
                ),
                status=discord.Status.online
            )
            # Then start Twitch bot
            await self.twitch_bot.start()
        except Exception as e:
            print(f"Failed to start Twitch bot or set presence: {e}")

    async def lastspawn(self, interaction: discord.Interaction):
        spawn = await self.db.get_last_spawn()
        if (spawn):
            embed = discord.Embed(
                title=f"Last Spawn: {spawn['name']}",
                color=self.theme_manager.get_type_color(spawn['types'].split()[0])
            )
            embed.add_field(name="Details", value=f"Tier: {spawn['tier']}\nTypes: {spawn['types']}")
            embed.set_footer(text=f"Spawned at: {spawn['timestamp']}")
            await interaction.response.send_message(embed=embed, view=PokemonView(self))
        else:
            await interaction.response.send_message("No recent spawns found!")

    async def stats(self, interaction: discord.Interaction):
        stats = await self.db.get_spawn_stats()
        embed = discord.Embed(
            title="Pokemon Spawn Statistics",
            color=0x2ECC71,
            description=f"Total Spawns: {stats['total_spawns']}\n"
                       f"Unique Pokemon: {stats['unique_pokemon']}\n"
                       f"Shiny Encounters: {stats['total_shinies']}"
        )
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed)
        else:
            await interaction.response.send_message(embed=embed)

    async def rarest(self, interaction: discord.Interaction):
        rarest = await self.db.get_rarest_spawns()
        embed = discord.Embed(title="Rarest Pokemon Spawns", color=0xFF0000)
        for pokemon in rarest:
            embed.add_field(
                name=pokemon['name'],
                value=f"Spawns: {pokemon['count']}\nShinies: {pokemon['shinies']}\n"
                      f"Last seen: {pokemon['last_seen']}",
                inline=False
            )
        await interaction.response.send_message(embed=embed)

    async def shinies(self, interaction: discord.Interaction):
        shinies = await self.db.get_recent_shinies()
        embed = discord.Embed(title="✨ Recent Shiny Spawns ✨", color=0xFFD700)
        for shiny in shinies:
            embed.add_field(
                name=shiny['name'],
                value=f"Tier: {shiny['tier']}\nTypes: {shiny['types']}\n"
                      f"Found: {shiny['timestamp']}",
                inline=False
            )
        await interaction.response.send_message(embed=embed)

    async def post_pokemon_info(self):
        await self.wait_until_ready()
        
        while not self.is_closed():
            if self.twitch_bot and self.twitch_bot.combined_info:
                try:
                    # Get list of all guilds and their configured channels
                    for guild in self.guilds:
                        channel_id = await self.db.get_server_channel(str(guild.id))
                        if channel_id:
                            channel = self.get_channel(int(channel_id))
                            if channel:
                                view = PokemonView(self)
                                await channel.send(embed=self.twitch_bot.combined_info, view=view)
                    
                    self.twitch_bot.combined_info = None
                except Exception as e:
                    print(f"Error sending to Discord: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    check_bot_authorized()
    client = DiscordBot()  # Remove the intents parameter since we handle it in __init__
    try:
        client.run(DISCORD_BOT_TOKEN)
    except discord.errors.LoginFailure:
        print("\nERROR: Invalid Discord bot token")
        print("Please check your DISCORD_BOT_TOKEN in .env")
    except Exception as e:
        print(f"\nError starting bot: {e}")
