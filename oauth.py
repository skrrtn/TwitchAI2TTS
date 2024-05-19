import requests

def get_oauth_token(client_id, client_secret):
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }

    response = requests.post(url, params=params)
    if response.status_code == 200:
        data = response.json()
        oauth_token = data['access_token']
        return oauth_token
    else:
        print('Failed to get OAuth token')
        return None

# Replace 'YOUR_CLIENT_ID' and 'YOUR_CLIENT_SECRET' with your actual Twitch client ID and client secret
client_id = 'you_client_id'
client_secret = 'your_client_secret'

oauth_token = get_oauth_token(client_id, client_secret)
if oauth_token:
    print('OAuth token:', oauth_token)