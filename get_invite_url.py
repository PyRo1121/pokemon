from config import DISCORD_CLIENT_ID

invite_url = f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&permissions=274878221312&scope=bot%20applications.commands"

print("\nYour Discord Bot Invite URL:")
print("=" * 50)
print(invite_url)
print("=" * 50)
print("\nShare this URL with others to let them add the bot to their servers!")
