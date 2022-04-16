import emoji

from .commons import commons as c
from .controls import TrackList, AlbumList, ArtistList, ltFIND, ltFAV


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


def find_artists(update, context):
    search_str = " ".join(context.args)
    artists = c.jamAPI.search_artists(context.args)
    data = ArtistList.create(items=artists, search_str=search_str, list_type=ltFIND)
    update.message.reply_text(**ArtistList.build_message_attrs(data))


def find_albums(update, context):
    search_str = " ".join(context.args)
    albums = c.jamAPI.search_artists(context.args)
    data = AlbumList.create(items=albums, search_str=search_str, list_type=ltFIND)
    update.message.reply_text(**AlbumList.build_message_attrs(data))


def find_tracks(update, context):
    search_str = " ".join(context.args)
    tracks = c.jamAPI.search_tracks(context.args)
    data = TrackList.create(items=tracks, search_str=search_str, list_type=ltFIND)
    update.message.reply_text(**TrackList.build_message_attrs(data))


def fav_artists(update, context):
    user_id = update.effective_user
    artists = c.dbAPI.get_fav_artists(user_id)
    data = ArtistList.create(items=artists, user_id=user_id, list_type=ltFAV)
    # ArtistList.send_message(data)


def fav_albums(update, context):
    user_id = update.effective_user
    albums = c.dbAPI.get_fav_artists(user_id)
    data = AlbumList.create(items=albums, user_id=user_id, list_type=ltFAV)
    # AlbumList.send_message(data)


def fav_tracks(update, context):
    user_id = update.effective_user
    tracks = c.dbAPI.get_fav_tracks(user_id)
    data = TrackList.create(items=tracks, user_id=user_id, list_type=ltFAV)
    # TrackList.send_message(data)
