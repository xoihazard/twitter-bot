# Twitter bot

A simple Twitter bot that randomly posts images in a specified folder.

## Requirements

- Twitter developer account (developer.twitter.com)
- Python 3
    - requests_oauthlib
    - tweepy

## Setup

### Install requirements

```bash
pip install requests_oauthlib tweepy
```

### Clone the repository

```bash
git clone https://github.com/xoihazard/twitter-bot.git
```

### Create settings.ini

Copy `settings.example.ini` to `settings.ini` and edit the following section.

```setting.ini
[Twitter API]
bearer_token = (Bearer token)
api_key = (Consumer API Key)
api_key_secret = (Consumer API Secret)
```

Consumer API keys are obtained at [developer.twitter.com](https://developer.twitter.com).

### Authorization

Get an access token with the posting account. In your browser, you must be logged into the account you use to post.

```bash
python3 get_token.py
```

Open the `https://api.twitter.com` link in your browser and enter the PIN displayed on your browser after verification.

```
Got OAuth token: XXX_XXXXXXXXXXXXXXXXXXXXXXX
Please go here and authorize: https://api.twitter.com/oauth/authorize?oauth_token=XXX_XXXXXXXXXXXXXXXXXXXXXXX
Paste the PIN here: 012345 <-- paste PIN from your browser
```

If successful, `access_token` and `access_token_secret` will be automatically added to `settings.ini`.

### Create data directory

Create directories with the following structure.

- twitter-bot/
    - data/
        - 1st_stockpile/
            - a great picture 1.jpg
            - a great picture 2.jpg
            - ...
        - 2nd_stockpile/
            - a great picture 3.jpg
            - a great picture 4.jpg
            - ...
        - posted/
        - text/
            - tweet1.txt
            - tweet2.txt
            - ...
        
Add the following to `settings.ini`.

```settings.ini
[Path]
stockpile_dirs = [ "data/1st_stockpile", "data/2nd_stockpile" ]
posted_dir = data/posted
text_dir = data/text
```

- The directories specified in `stockpile_dirs` are scanned in order, and randomly picked up an image file (png/jpg/gif) to post.
- Posted images are moved to `posted_dir` with the UNIX time added to the file name.
- The text of the tweet will be the content of the *.txt file randomly picked from `text_dir`.

## Run

Just run post.py.

```
python3 post.py
```

## License

MIT License