from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Environment variables
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

@app.route('/callback')
def callback():
    """Handle Discord OAuth2 callback"""
    code = request.args.get('code')
    
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
            return '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>✅ Verification Complete</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                        margin: 0;
                        padding: 0;
                        background: linear-gradient(135deg, #7289da 0%, #5865f2 100%);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    .container {
                        background: rgba(255, 255, 255, 0.95);
                        padding: 40px;
                        border-radius: 20px;
                        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                        text-align: center;
                        max-width: 500px;
                        width: 90%;
                    }
                    .success-icon {
                        font-size: 80px;
                        color: #43b581;
                        margin-bottom: 20px;
                    }
                    h1 {
                        color: #23272a;
                        margin-bottom: 10px;
                    }
                    p {
                        color: #4f545c;
                        line-height: 1.6;
                        margin-bottom: 20px;
                    }
                    .close-btn {
                        background: #43b581;
                        color: white;
                        border: none;
                        padding: 12px 30px;
                        border-radius: 8px;
                        font-size: 16px;
                        font-weight: 600;
                        cursor: pointer;
                        transition: background 0.2s;
                    }
                    .close-btn:hover {
                        background: #3ca374;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="success-icon">✅</div>
                    <h1>Authorization Successful!</h1>
                    <p>You have granted the necessary permissions for server verification.</p>
                    <p>You can now return to Discord and complete the verification process.</p>
                    <button class="close-btn" onclick="window.close()">Close Window</button>
                </div>
                
                <script>
                    // Auto-close after 8 seconds
                    setTimeout(() => {
                        window.close();
                    }, 8000);
                    
                    // Notify opener if exists
                    if (window.opener) {
                        window.opener.postMessage('discord_oauth_complete', '*');
                    }
                </script>
            </body>
            </html>
            ''', 200
        else:
            return f'''
            <html>
            <body style="font-family: Arial; padding: 50px; text-align: center;">
                <h1 style="color: #ed4245;">❌ Authorization Failed</h1>
                <p>Error {response.status_code}: {response.text}</p>
                <p><a href="/">Try again</a></p>
            </body>
            </html>
            ''', 400
            
    except Exception as e:
        return f'''
        <html>
        <body style="font-family: Arial; padding: 50px; text-align: center;">
            <h1 style="color: #ed4245;">❌ Server Error</h1>
            <p>{str(e)}</p>
        </body>
        </html>
        ''', 500

@app.route('/')
def home():
    return '''
    <html>
    <head>
        <title>Discord Verification</title>
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
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🔐 Discord Verification Server</h1>
            <p>This server handles Discord OAuth2 callbacks for server verification.</p>
            <p>To verify, use the verification command in your Discord server.</p>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    port = int(os.getenv("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
