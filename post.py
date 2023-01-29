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
            return filename

    return None


def post(src_filename, text):
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

    config = configparser.RawConfigParser()
    with open(CONFIG_FILENAME, "r", encoding="utf-8") as f:
        config.read_file(f)

    api_key = config.get("Twitter API", "api_key")
    api_key_secret = config.get("Twitter API", "api_key_secret")
    access_token = config.get("Twitter API", "access_token")
    access_token_secret = config.get("Twitter API", "access_token_secret")

    auth = tweepy.OAuth1UserHandler(
        api_key,
        api_key_secret,
        access_token,
        access_token_secret,
    )

    api = tweepy.API(auth)

    stockpile_dirs = json.loads(config.get("Path", "stockpile_dirs"))
    posted_dir = config.get("Path", "posted_dir")
    text_dir = config.get("Path", "text_dir")

    text_filename = pickup_random_file(f"{text_dir}/*", r".*\.txt$")

    if text_filename:
        with open(text_filename, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = ""

    for stockpile_dir in stockpile_dirs:
        media_filename = pickup_random_file(
            f"{stockpile_dir}/*", r".*\.(jpe?g|png|gif)$")
        if media_filename:
            post(media_filename, text)
            break
