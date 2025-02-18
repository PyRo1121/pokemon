from flask import Flask, request, redirect, session, render_template
from config import *
import requests
import secrets

app = Flask(__name__, 
    template_folder='templates',
    static_folder='static'
)
app.secret_key = secrets.token_hex(16)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth/twitch')
def twitch_auth():
    state = secrets.token_hex(16)
    session['state'] = state
    return redirect(
        f"https://id.twitch.tv/oauth2/authorize"
        f"?client_id={TWITCH_CLIENT_ID}"
        f"&redirect_uri={TWITCH_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=chat:read chat:edit channel:moderate channel:read:redemptions"
        f"&state={state}"
    )

@app.route('/auth/discord')
def discord_auth():
    return redirect(
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={DISCORD_CLIENT_ID}"
        f"&permissions=274878221312"
        f"&scope=bot%20applications.commands"
        f"&redirect_uri={DISCORD_REDIRECT_URI}"
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
