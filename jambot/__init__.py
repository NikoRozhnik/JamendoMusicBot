import logging
import os
from configparser import ConfigParser

import emoji
from telegram.ext import (  # InvalidCallbackData,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    PicklePersistence,
    Updater,
)

from .commands import fav_albums, fav_artists, fav_tracks, find_albums, find_artists, find_tracks, handle_button
from .commons import commons as c
from .db import DataBaseAPI
from .jamendo import JamendoAPI


__all__ = ["main", "get_variables"]

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)


DB_NAME = "jambot.db"
CONFIG_NAME = "jambot.conf"
PERISTENCE_NAME = "jambot.persist"

wellcome_txt = emoji.emojize(
    """*Wellcome!*

I'm *jamendo musical bot* :musical_score:

I will help you find music on [Jamendo Music](http://www.jamendo.com/) and save your favorites artists, albums and tracks
"""
)

help_txt = emoji.emojize(
    """jamendo musical bot :musical_score: commands:

/help - this help
/artists <search_str> - find artists
/albums <search_str> - find albums
/tracks <search_str> - find tracks
/fav_artists - show favorite artist list
/fav_albums - show favorite album list
/fav_tracks - show favorite track list
"""
)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=wellcome_txt, parse_mode="Markdown")


def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_txt)


def main():
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    logging.getLogger(__name__)

    conf = ConfigParser()
    conf.read(CONFIG_NAME)
    try:
        defaults = dict(conf["defaults"])
    except KeyError:
        defaults = {}

    CLIENT_ID = os.getenv("JAMENDO_CLIENT_ID")
    if not CLIENT_ID:
        raise ValueError("The JAMENDO_CLIENT_ID environment variable was not found.")

    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("The TELEGRAM_BOT_TOKEN environment variable was not found.")

    c.jamAPI = JamendoAPI(CLIENT_ID, defaults)
    c.dbAPI = DataBaseAPI(DB_NAME)
    ppersist = PicklePersistence(filename=PERISTENCE_NAME, store_callback_data=True)
    updater = Updater(token=BOT_TOKEN, persistence=ppersist, arbitrary_callback_data=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("artists", find_artists))
    dispatcher.add_handler(CommandHandler("albums", find_albums))
    dispatcher.add_handler(CommandHandler("tracks", find_tracks))
    dispatcher.add_handler(CommandHandler("artists", fav_artists))
    dispatcher.add_handler(CommandHandler("albums", fav_albums))
    dispatcher.add_handler(CommandHandler("tracks", fav_tracks))
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), find_tracks))
    dispatcher.add_handler(CallbackQueryHandler(handle_button))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
