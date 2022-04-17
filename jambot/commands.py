import emoji

from .commons import commons as c
from .controls import TrackList, AlbumList, ArtistList, ltFIND, ltFAV


wellcome_txt = emoji.emojize(
    """*Привет!*

Я - *jamendo musical bot* :musical_score:

Я помогу тебе искать музыку на [Jamendo Music](http://www.jamendo.com/)
 и сохранять списки любимых исполнителей, альбомов и записей
"""
)

help_txt = emoji.emojize(
    """jamendo musical bot :musical_score: commands:

/help - справка о командах
/artists <search_str> - найти исполнителей
/albums <search_str> - найти альбомы
/tracks <search_str> - найти записи
/fav_artists - список избранных исполнителей
/fav_albums - список избранных альбомов
/fav_tracks - список избранныз команд
"""
)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=wellcome_txt, parse_mode="Markdown")


def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_txt)


def find_artists(update, context):
    search_str = " ".join(context.args)
    artists = c.jamAPI.search_artists(context.args)
    artist_list = ArtistList(items=artists, search_str=search_str, list_type=ltFIND)
    update.message.reply_text(**artist_list.build_message_attrs())


def find_albums(update, context):
    search_str = " ".join(context.args)
    albums = c.jamAPI.search_albums(context.args)
    album_list = AlbumList(items=albums, search_str=search_str, list_type=ltFIND)
    update.message.reply_text(**album_list.build_message_attrs())


def find_tracks(update, context):
    search_str = " ".join(context.args)
    tracks = c.jamAPI.search_tracks(context.args)
    track_list = TrackList(items=tracks, search_str=search_str, list_type=ltFIND)
    update.message.reply_text(**track_list.build_message_attrs())


def fav_artists(update, context):
    user = update.effective_user
    id = user["id"]
    name = user["first_name"] + " " + user["last_name"]
    artists = c.dbAPI.get_fav_artists(id)
    artist_list = ArtistList(items=artists, user_id=id, user_name=name, list_type=ltFAV)
    update.message.reply_text(**artist_list.build_message_attrs())


def fav_albums(update, context):
    user = update.effective_user
    id = user["id"]
    name = user["first_name"] + " " + user["last_name"]
    albums = c.dbAPI.get_fav_albums(id)
    album_list = AlbumList(items=albums, user_id=id, user_name=name, list_type=ltFAV)
    update.message.reply_text(**album_list.build_message_attrs())


def fav_tracks(update, context):
    user = update.effective_user
    id = user["id"]
    name = user["first_name"] + " " + user["last_name"]
    tracks = c.dbAPI.get_fav_tracks(id)
    track_list = TrackList(items=tracks, user_id=id, user_name=name, list_type=ltFAV)
    update.message.reply_text(**track_list.build_message_attrs())
