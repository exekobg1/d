from flask import Flask, request, redirect
import requests
import os
import json

app = Flask(__name__)

# Environment variables
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
BOT_WEBHOOK_URL = os.getenv("BOT_WEBHOOK_URL", "http://localhost:8080/webhook")  # Your bot's URL

@app.route('/callback')
def callback():
    """Handle Discord OAuth2 callback and forward token to bot"""
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code:
        return "No authorization code", 400
    
    # Exchange code for token
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        response = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access_token']
            
            # Get user info
            user_response = requests.get(
                'https://discord.com/api/users/@me',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                user_id = user_data.get('id')
                
                # Parse state for guild_id
                guild_id = None
                if state and ':' in state:
                    try:
                        user_id_from_state, guild_id_from_state = state.split(':')
                        guild_id = guild_id_from_state
                    except:
                        pass
                
                # Send token to bot
                send_to_bot(user_id, access_token, guild_id)
                
                return '''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>✅ Verification Complete</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            text-align: center;
                            padding: 50px;
                            background: linear-gradient(135deg, #43b581 0%, #3ca374 100%);
                            color: white;
                        }
                        .container {
                            background: rgba(255, 255, 255, 0.1);
                            padding: 40px;
                            border-radius: 20px;
                            backdrop-filter: blur(10px);
                            max-width: 500px;
                            margin: 0 auto;
                        }
                        .success { font-size: 60px; margin: 20px; }
                        h1 { margin-bottom: 20px; }
                        .status {
                            background: rgba(0,0,0,0.2);
                            padding: 15px;
                            border-radius: 10px;
                            margin: 20px;
                            text-align: left;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="success">✅</div>
                        <h1>Verification Complete!</h1>
                        <p>Your authorization was successful.</p>
                        
                        <div class="status">
                            <p><strong>Token Status:</strong> Sent to bot</p>
                            <p><strong>User ID:</strong> {}</p>
                            <p><strong>Token:</strong> {}...</p>
                        </div>
                        
                        <p>You can now return to Discord.</p>
                        <p><small>This window will close in 5 seconds...</small></p>
                    </div>
                    
                    <script>
                        setTimeout(() => {{
                            window.close();
                        }}, 5000);
                        
                        // Notify Discord
                        if (window.opener) {{
                            window.opener.postMessage('oauth_complete', '*');
                        }}
                    </script>
                </body>
                </html>
                '''.format(user_id, access_token[:20])
            else:
                return "Failed to get user info", 400
        else:
            return f"Token exchange failed: {response.text}", 400
            
    except Exception as e:
        return f"Server error: {str(e)}", 500

def send_to_bot(user_id: str, access_token: str, guild_id: str = None):
    """Send token to bot's webhook endpoint"""
    try:
        payload = {
            'user_id': user_id,
            'access_token': access_token,
            'guild_id': guild_id,
            'timestamp': os.times().user,
            'source': 'railway'
        }
        
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(
            BOT_WEBHOOK_URL,
            json=payload,
            headers=headers,
            timeout=5
        )
        
        print(f"✅ Sent token for user {user_id} to bot: {response.status_code}")
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Failed to send to bot: {e}")
        return False

@app.route('/')
def home():
    return '''
    <html>
    <head>
        <title>Discord OAuth2 Server</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background: #36393f;
                color: white;
            }
            .card {
                background: #2f3136;
                padding: 40px;
                border-radius: 10px;
                display: inline-block;
                margin: 20px;
            }
            .webhook-status {
                background: #202225;
                padding: 15px;
                border-radius: 5px;
                margin: 20px;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🔐 Discord OAuth2 Server</h1>
            <p>This server handles Discord OAuth2 callbacks.</p>
            <p>Tokens are sent to: <code>{}</code></p>
            
            <div class="webhook-status">
                <h3>📡 Webhook Status</h3>
                <p>Bot Webhook URL: <code>{}</code></p>
                <p>Make sure your bot is listening at this URL!</p>
            </div>
        </div>
    </body>
    </html>
    '''.format(BOT_WEBHOOK_URL, BOT_WEBHOOK_URL)

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
