import logging
import os
from configparser import ConfigParser

from telegram.ext import CallbackQueryHandler, CommandHandler, PicklePersistence, Updater

from .commands import fav_albums, fav_artists, fav_tracks, find_albums, find_artists, find_tracks, help, start
from .commons import commons as c
from .controls import sign2ctrl
from .db import DataBaseAPI
from .jamendo import JamendoAPI


__all__ = ["main"]

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

DB_NAME = "jambot.db"
CONFIG_NAME = "jambot.conf"
PERISTENCE_NAME = "jambot.persist"


def handle_query(update, context):
    query = update.callback_query
    query.answer()
    sign2ctrl[query.data[0]["sign"]].handle(query)


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
    dispatcher.add_handler(CommandHandler("fav_artists", fav_artists))
    dispatcher.add_handler(CommandHandler("fav_albums", fav_albums))
    dispatcher.add_handler(CommandHandler("fav_tracks", fav_tracks))
    dispatcher.add_handler(CallbackQueryHandler(handle_query))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
