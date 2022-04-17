import emoji
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from .commons import commons as c
from .utils import get_thumb

_sign2ctrl = {}

# тип списка (поиск или избранные - разные заголовки)
ltFIND = 0
ltFAV = 1

MENU_FIRST = -1
MENU_PREV = -2
MENU_NEXT = -3
MENU_LAST = -4
MENU_CLOSE = -5
MENU_FAV = -6
MENU_UNFAV = -7


def get_object(data):
    global _sign2ctrl
    return _sign2ctrl[data["sign"]](data)


class BaseControl:
    sign = ""

    def __init__(self, data=None, **kwargs):
        if data:
            self.data = data
        else:
            self.data = {}
        for k, v in kwargs.items():
            if k not in self.data:
                self.data[k] = v
        self.data["sign"] = self.sign

    def get_data(self):
        return self.data

    @staticmethod
    def get_button_id(query):
        return query.data[1]

    def handle(self, query):
        if self.get_button_id(query) == MENU_CLOSE:
            query.delete_message()
            return True
        else:
            return False

    def build_message_attrs(self):
        return {}


class Track(BaseControl):
    sign = "Track"

    def init(self, data=None, **kwargs):
        super().__init__(data, **kwargs)

    def handle(self, query):
        if not super().handle(query):
            button_id = self.get_button_id(query)
            user_id = query.from_user.id
            if button_id == MENU_FAV:
                c.dbAPI.add_fav_track(user_id, self.data)
                return True
            elif button_id == MENU_UNFAV:
                c.dbAPI.del_fav_track(user_id, self.data["id"])
                return True
            else:
                return False

    def build_keyboard(self):
        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(emoji.emojize(":heart_suit:"), callback_data=(self.data, MENU_FAV)),
                    InlineKeyboardButton(emoji.emojize(":broken_heart:"), callback_data=(self.data, MENU_UNFAV)),
                    InlineKeyboardButton(emoji.emojize(":cross_mark:"), callback_data=(self.data, MENU_CLOSE)),
                ]
            ]
        )

    def build_message_attrs(self):
        return {
            "audio": self.data["audiodownload"],
            "duration": self.data["duration"],
            "thumb": get_thumb(self.data["album_image"]),
            "reply_markup": self.build_keyboard(),
        }


class BaseList(BaseControl):
    def __init__(self, data=None, **kwargs):
        super().__init__(data, **kwargs)
        if "offset" not in self.data:
            self.data["offset"] = 0
        self.data["num_items"] = len(self.data["items"])
        if "menu_size" not in self.data:
            self.data["menu_size"] = 10

    def format_item(self, item):
        return item["name"]

    def build_message_attrs(self):
        return {"text": self.build_text(), "reply_markup": self.build_keyboard(), "parse_mode": "Markdown"}

    def build_text(self):
        total_r = self.data["num_items"]
        if not total_r:
            beg_r = 0
            end_r = 0
        else:
            beg_r = self.data["offset"] + 1
            if total_r < self.data["menu_size"]:
                end_r = total_r
            else:
                end_r = self.data["offset"] + self.data["menu_size"]
        return f"{self.data['title']}\n({beg_r} - {end_r} из {total_r})"

    def build_keyboard(self):
        btns = []
        for i in range(min(self.data["menu_size"], self.data["num_items"])):
            offset = self.data["offset"] + i
            name = self.format_item(self.data["items"][offset])
            btns.append([InlineKeyboardButton(f"{offset+1}. {name}", callback_data=(self.data, i))])
        btns.extend(self.build_ctrl_buttons())
        return InlineKeyboardMarkup(btns)

    def build_ctrl_buttons(self):
        return [
            [
                InlineKeyboardButton(emoji.emojize(":last_track_button:"), callback_data=(self.data, MENU_FIRST)),
                InlineKeyboardButton(emoji.emojize(":reverse_button:"), callback_data=(self.data, MENU_PREV)),
                InlineKeyboardButton(emoji.emojize(":play_button:"), callback_data=(self.data, MENU_NEXT)),
                InlineKeyboardButton(emoji.emojize(":next_track_button:"), callback_data=(self.data, MENU_LAST)),
                InlineKeyboardButton(emoji.emojize(":cross_mark:"), callback_data=(self.data, MENU_CLOSE)),
            ]
        ]

    def handle(self, query):
        if super().handle(query):
            return True
        else:
            button_id = self.get_button_id(query)
            if button_id == MENU_CLOSE:
                query.delete_message()
            else:
                if button_id == MENU_FIRST:
                    self.data["offset"] = 0
                elif button_id == MENU_PREV:
                    self.data["offset"] -= self.data["menu_size"]
                    if self.data["offset"] < 0:
                        self.data["offset"] = 0
                elif button_id == MENU_NEXT:
                    self.data["offset"] += self.data["menu_size"]
                    if self.data["offset"] + self.data["menu_size"] > self.data["num_items"]:
                        self.data["offset"] = self.data["num_items"] - self.data["menu_size"]
                        if self.data["offset"] < 0:
                            self.data["offset"] = 0
                elif button_id == MENU_LAST:
                    self.data["offset"] = self.data["num_items"] - self.data["menu_size"]
                    if self.data["offset"] < 0:
                        self.data["offset"] = 0
                else:
                    return False
                attrs = self.build_message_attrs()
                if "caption" in attrs:
                    query.edit_message_caption(**attrs)
                else:
                    query.edit_message_text(**attrs)
            return True


class ArtistList(BaseList):
    sign = "ArtistList"

    def __init__(self, data=None, **kwargs):
        super().__init__(data, **kwargs)
        if "search_str" in self.data:
            self.data["title"] = f"Поиск исполнителей: *{self.data['search_str']}*"
        if "user_name" in self.data:
            self.data["title"] = f"*{self.data['user_name']}.* Избранные исполнители"

    def format_item(self, item):
        return f"{item['name']}"

    def handle(self, query):
        if super().handle(query):
            return True
        else:
            button_id = self.get_button_id(query)
            if button_id >= 0:
                artist = self.data["items"][self.data["offset"] + button_id]
                albums = c.jamAPI.get_artist_albums(artist["id"])
                artist_albums = ArtistAlbums(header=artist, items=albums)
                photo = artist_albums.data["header"]["image"]
                if photo:
                    query.bot.send_photo(query.message.chat_id, photo=photo, **artist_albums.build_message_attrs())
                else:
                    query.bot.send_message(query.message.chat_id, **artist_albums.build_message_attrs())
                return True
        return False


class AlbumList(BaseList):
    sign = "AlbumList"

    def __init__(self, data=None, **kwargs):
        super().__init__(data, **kwargs)
        if "search_str" in self.data:
            self.data["title"] = f"Поиск альбомов: *{self.data['search_str']}*"
        if "user_name" in self.data:
            self.data["title"] = f"*{self.data['user_name']}.* Избранные альбомы"

    def format_item(self, item):
        return f"{item['name']} - {item['artist_name']}"

    def handle(self, query):
        if super().handle(query):
            return True
        else:
            button_id = self.get_button_id(query)
            if button_id >= 0:
                album = self.data["items"][self.data["offset"] + button_id]
                tracks = c.jamAPI.get_album_tracks(album["id"])
                album_tracks = AlbumTracks(header=album, items=tracks)
                photo = album_tracks.data["header"]["image"]
                if photo:
                    query.bot.send_photo(query.message.chat_id, photo=photo, **album_tracks.build_message_attrs())
                else:
                    query.bot.send_message(query.message.chat_id, **album_tracks.build_message_attrs())
                return True
        return False


class TrackList(BaseList):
    sign = "TrackList"

    def __init__(self, data=None, **kwargs):
        super().__init__(data, **kwargs)
        if "search_str" in self.data:
            self.data["title"] = f"Поиск записей: *{self.data['search_str']}*"
        if "user_name" in self.data:
            self.data["title"] = f"*{self.data['user_name']}.* Избранные записи"

    def format_item(self, item):
        return f"{item['name']} - {item['artist_name']}"

    def handle(self, query):
        if super().handle(query):
            return True
        else:
            button_id = self.get_button_id(query)
            if button_id >= 0:
                track = Track(**self.data["items"][self.data["offset"] + button_id])
                query.bot.send_audio(query.message.chat_id, **track.build_message_attrs())
                return True
        return False


class FavBaseList(BaseList):
    def __init__(self, data=None, **kwargs):
        kwargs["menu_size"] = 5
        super().__init__(data, **kwargs)

    def build_ctrl_buttons(self):
        return [
            [
                InlineKeyboardButton(emoji.emojize(":heart_suit:"), callback_data=(self.data, MENU_FAV)),
                InlineKeyboardButton(emoji.emojize(":broken_heart:"), callback_data=(self.data, MENU_UNFAV)),
            ],
            [
                InlineKeyboardButton(emoji.emojize(":last_track_button:"), callback_data=(self.data, MENU_FIRST)),
                InlineKeyboardButton(emoji.emojize(":reverse_button:"), callback_data=(self.data, MENU_PREV)),
                InlineKeyboardButton(emoji.emojize(":play_button:"), callback_data=(self.data, MENU_NEXT)),
                InlineKeyboardButton(emoji.emojize(":next_track_button:"), callback_data=(self.data, MENU_LAST)),
                InlineKeyboardButton(emoji.emojize(":cross_mark:"), callback_data=(self.data, MENU_CLOSE)),
            ],
        ]

    def build_message_attrs(self):
        attrs = {
            "reply_markup": self.build_keyboard(),
            "parse_mode": "Markdown",
        }
        if self.data["header"]["image"]:
            attrs["caption"] = self.build_text()
        else:
            attrs["text"] = self.build_text()
        return attrs


class ArtistAlbums(FavBaseList):
    sign = "ArtistAlbums"

    def build_text(self):
        txt = f"Альбомы исполнителя *{self.data['header']['name']}*"
        if self.data["header"]["website"]:
            txt += f"\nСайт: [{self.data['header']['website']}]"
        return txt

    def handle(self, query):
        if not super().handle(query):
            button_id = self.get_button_id(query)
            user_id = query.from_user.id
            if button_id >= 0:
                album = self.data["items"][self.data["offset"] + button_id]
                tracks = c.jamAPI.get_album_tracks(album["id"])
                album_tracks = AlbumTracks(header=album, items=tracks)
                photo = album_tracks.data["header"]["image"]
                if photo:
                    query.bot.send_photo(query.message.chat_id, photo=photo, **album_tracks.build_message_attrs())
                else:
                    query.bot.send_message(query.message.chat_id, **album_tracks.build_message_attrs())
                return True
            else:
                if button_id == MENU_FAV:
                    c.dbAPI.add_fav_artist(user_id, self.data["header"])
                    return True
                elif button_id == MENU_UNFAV:
                    c.dbAPI.del_fav_artist(user_id, self.data["header"]["id"])
                    return True
                else:
                    return False


class AlbumTracks(FavBaseList):
    sign = "AlbumTracks"

    def build_text(self):
        txt = f"Альбом *{self.data['header']['name']}*"
        if self.data["header"]["artist_name"]:
            txt += f"\nИсполнитель: *{self.data['header']['artist_name']}*"
        return txt

    def handle(self, query):
        if not super().handle(query):
            button_id = self.get_button_id(query)
            user_id = query.from_user.id
            if button_id >= 0:
                track = Track(**self.data["items"][self.data["offset"] + button_id])
                query.bot.send_audio(query.message.chat_id, **track.build_message_attrs())
                return True
            else:
                if button_id == MENU_FAV:
                    c.dbAPI.add_fav_album(user_id, self.data["header"])
                    return True
                elif button_id == MENU_UNFAV:
                    c.dbAPI.del_fav_album(user_id, self.data["header"]["id"])
                    return True
                else:
                    return False


for cls in (Track, TrackList, AlbumList, ArtistList, ArtistAlbums, AlbumTracks):
    _sign2ctrl[cls.sign] = cls
