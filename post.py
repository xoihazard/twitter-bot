import os
import shutil
import re
import glob
import time
import random
import configparser
import json
import tweepy

CONFIG_FILENAME = "settings.ini"


def pickup_random_file(pathname, pattern=r".*"):
    filenames = glob.glob(pathname)
    random.shuffle(filenames)

    for filename in filenames:
        if re.match(pattern, filename):
            return os.path.abspath(filename)

    return None


def post(api, src_filename, text):
    src_basename = os.path.basename(src_filename)
    prefix = int(time.time())
    dst_basename = f"{prefix} {src_basename}"
    dst_filename = os.path.join(posted_dir, dst_basename)

    print(f"uploading: {src_filename}")
    media = api.media_upload(src_filename)
    api.update_status(text, media_ids=[media.media_id])

    shutil.move(src_filename, dst_filename)
    print(f"moved: {dst_filename}")


if __name__ == "__main__":
    abspath = os.path.abspath(__file__)
    os.chdir(os.path.dirname(abspath))

    # Read config
    config = configparser.RawConfigParser()
    with open(CONFIG_FILENAME, "r", encoding="utf-8") as f:
        config.read_file(f)

    api_key = config.get("Twitter API", "api_key")
    api_key_secret = config.get("Twitter API", "api_key_secret")
    access_token = config.get("Twitter API", "access_token")
    access_token_secret = config.get("Twitter API", "access_token_secret")

    stockpile_dirs = json.loads(config.get("Path", "stockpile_dirs"))
    posted_dir = config.get("Path", "posted_dir")
    text_dir = config.get("Path", "text_dir")

    # Initialize tweepy
    auth = tweepy.OAuth1UserHandler(
        api_key,
        api_key_secret,
        access_token,
        access_token_secret,
    )

    api = tweepy.API(auth)

    # Random pickup of text and image filenames
    text_filename = pickup_random_file(f"{text_dir}/*", r".*\.(txt|py)$")
    media_filename = None

    for stockpile_dir in stockpile_dirs:
        media_filename = pickup_random_file(
            f"{stockpile_dir}/*", r".*\.(jpe?g|png|gif)$")
        if media_filename:
            break

    # Generate tweet text
    tweet = ""

    if text_filename:
        with open(text_filename, "r", encoding="utf-8") as f:
            text = f.read()

        if re.match(r".*\.py$", text_filename):
            result = {}
            exec(text, result)

            if "tweet" in result:
                tweet = result["tweet"](media_filename)
        else:
            tweet = text

    # Tweet if image file is available
    if media_filename:
        post(api, media_filename, tweet)
