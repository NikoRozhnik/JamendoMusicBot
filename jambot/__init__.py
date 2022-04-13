import os

import emoji
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from .commands import albums, artists, find_albums, find_artists, find_tracks, tracks
from .jamendo import JamendoAPI
from .db import DataBaseAPI

__all__ = ["main"]


DB_NAME = "jamendo.db"

wellcome_txt = emoji.emojize(
    """*Wellcome!*

I'm *jamendo musical bot* :musical_score:

I will help you find music on [Jamendo Music](http://www.jamendo.com/) and save your favorites artists, albums and tracks
"""
)

help_txt = emoji.emojize(
    """jamendo musical bot :musical_score: commands:

/help - this help
/find_artists <search_str> - find artists
/find_albums <search_str> - find albums
/find_tracks <search_str> - find tracks
/artists - show favorite artist list
/albums - show favorite album list
/tracks - show favorite track list
"""
)

_jamAPI = None
_dbAPI = None


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=wellcome_txt, parse_mode="Markdown")
    context.bot_data["jamAPI"] = _jamAPI
    context.bot_data["dbAPI"] = _dbAPI


def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_txt)


def main():
    global _jamAPI, _dbAPI
    CLIENT_ID = os.getenv("JAMENDO_CLIENT_ID")
    if not CLIENT_ID:
        raise ValueError("The JAMENDO_CLIENT_ID environment variable was not found.")

    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("The TELEGRAM_BOT_TOKEN environment variable was not found.")

    _jamAPI = JamendoAPI(CLIENT_ID)
    _dbAPI = DataBaseAPI(DB_NAME)
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("find_artists", find_artists))
    dispatcher.add_handler(CommandHandler("find_albums", find_albums))
    dispatcher.add_handler(CommandHandler("find_tracks", find_tracks))
    dispatcher.add_handler(CommandHandler("artists", artists))
    dispatcher.add_handler(CommandHandler("albums", albums))
    dispatcher.add_handler(CommandHandler("tracks", tracks))
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), find_tracks))
    updater.start_polling()


if __name__ == "__main__":
    main()
