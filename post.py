import os
import shutil
import re
import glob
import random
import configparser
import json
import tweepy
import logging
from logging.handlers import TimedRotatingFileHandler

CONFIG_FILENAME = "settings.ini"
LOG_FILENAME = "log/post.log"


def pickup_random_file(pathname: str, pattern: str = r".*") -> str:
    filenames = glob.glob(pathname)
    random.shuffle(filenames)

    for filename in filenames:
        if re.match(pattern, filename):
            return os.path.abspath(filename)

    return None


def post(
    api: tweepy.API,
    client: tweepy.Client,
    src_filename: str,
    text: str,
    dst_dirname: str,
) -> None:
    src_basename = os.path.basename(src_filename)
    dst_filename = os.path.abspath(os.path.join(dst_dirname, src_basename))

    try:
        media = api.media_upload(src_filename)
        logging.info(f"Media file uploaded: {media.media_id}")

        response = client.create_tweet(text=text, media_ids=[media.media_id])
        logging.info(f"Tweeted: {response.data}")
    except Exception as error:
        logging.error(error)
    else:
        shutil.move(src_filename, dst_filename)
        logging.info(f"Media file moved: {dst_filename}")


def init_logging(log_filename: str) -> None:
    dirname = os.path.dirname(log_filename)
    os.makedirs(dirname, exist_ok=True)

    log_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    file_handler = TimedRotatingFileHandler(
        log_filename, when="midnight", backupCount=7, encoding="utf-8"
    )
    file_handler.suffix = "%Y-%m-%d"
    file_handler.setFormatter(log_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)

    logging.basicConfig(level=logging.INFO, handlers=[console_handler, file_handler])


def main(config_filename: str) -> None:
    if not os.path.exists(config_filename):
        logging.error(f"Config file not exist: {config_filename}")
        return

    # Read config
    config = configparser.RawConfigParser()
    with open(config_filename, "r", encoding="utf-8") as f:
        config.read_file(f)

    api_key = config.get("Twitter API", "api_key")
    api_key_secret = config.get("Twitter API", "api_key_secret")
    access_token = config.get("Twitter API", "access_token")
    access_token_secret = config.get("Twitter API", "access_token_secret")
    bearer_token = config.get("Twitter API", "bearer_token")

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

    tweepy_api = tweepy.API(auth)
    tweepy_client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=api_key,
        consumer_secret=api_key_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )

    # Random pickup of text and image filenames
    text_filename = pickup_random_file(f"{text_dir}/*", r".*\.(txt|py)$")
    media_filename = None

    for stockpile_dir in stockpile_dirs:
        media_filename = pickup_random_file(
            f"{stockpile_dir}/*", r".*\.(jpe?g|png|gif)$"
        )
        if media_filename:
            logging.info(f"Picked up media file: {media_filename}")
            break

    # Generate tweet text
    tweet = ""

    if text_filename:
        logging.info(f"Picked up text file: {text_filename}")

        with open(text_filename, "r", encoding="utf-8") as f:
            text = f.read()

        if re.match(r".*\.py$", text_filename):
            logging.info(f"Executing as Python script: {text_filename}")

            try:
                result = {}
                exec(text, result)

                if "tweet" in result:
                    tweet = result["tweet"](media_filename)
                    logging.info(f"Text generated: {tweet}")
                else:
                    logging.error("tweet() function does not exist.")
            except Exception as error:
                logging.error(error)
        else:
            tweet = text
            logging.info(f"Text loaded: {tweet}")

    # Tweet if image file is available
    if media_filename:
        post(tweepy_api, tweepy_client, media_filename, tweet, posted_dir)
    else:
        logging.error("Media file not found.")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    init_logging(LOG_FILENAME)
    main(CONFIG_FILENAME)
