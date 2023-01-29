import os
import configparser
from requests_oauthlib import OAuth1Session

CONFIG_FILENAME = "settings.ini"

abspath = os.path.abspath(__file__)
os.chdir(os.path.dirname(abspath))

# Read config
config = configparser.RawConfigParser()
with open(CONFIG_FILENAME, "r", encoding="utf-8") as f:
    config.read_file(f)

api_key = config["Twitter API"]["api_key"]
api_key_secret = config["Twitter API"]["api_key_secret"]

# Get request token
request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
oauth = OAuth1Session(api_key, client_secret=api_key_secret)

try:
    fetch_response = oauth.fetch_request_token(request_token_url)
except ValueError:
    print(
        "There may have been an issue with the consumer_key or consumer_secret you entered."
    )

resource_owner_key = fetch_response.get("oauth_token")
resource_owner_secret = fetch_response.get("oauth_token_secret")
print("Got OAuth token: %s" % resource_owner_key)

# Get authorization
base_authorization_url = "https://api.twitter.com/oauth/authorize"
authorization_url = oauth.authorization_url(base_authorization_url)
print("Please go here and authorize: %s" % authorization_url)
verifier = input("Paste the PIN here: ")

# Get the access token
access_token_url = "https://api.twitter.com/oauth/access_token"
oauth = OAuth1Session(
    api_key,
    client_secret=api_key_secret,
    resource_owner_key=resource_owner_key,
    resource_owner_secret=resource_owner_secret,
    verifier=verifier,
)
oauth_tokens = oauth.fetch_access_token(access_token_url)

config["Twitter API"]["access_token"] = oauth_tokens["oauth_token"]
config["Twitter API"]["access_token_secret"] = oauth_tokens["oauth_token_secret"]

# Save config
with open(CONFIG_FILENAME, "w", encoding="utf-8") as f:
    config.write(f)
