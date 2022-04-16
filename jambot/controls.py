import emoji
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


sign2ctrl = {}

# тип списка (поиск или избранные - разные заголовки)
ltFIND = 0
ltFAV = 1

MENU_FIRST = -1
MENU_PREV = -2
MENU_NEXT = -3
MENU_LAST = -4
MENU_CLOSE = -5
NAV_BUTTONS = (MENU_FIRST, MENU_PREV, MENU_NEXT, MENU_LAST, MENU_CLOSE)


class BaseControl:
    sign = ""

    @classmethod
    def create(cls, **kw_args):
        kw_args["sign"] = cls.sign
        return dict(kw_args)

    @classmethod
    def handle(cls, query):
        data, button_id = query.data
        if button_id == MENU_CLOSE:
            query.delete_message()
            return True
        else:
            return False

    @classmethod
    def build_message_attrs(cls, data):
        return {}


class Track(BaseControl):
    sign = "Track"

    @classmethod
    def create(cls, **kw_args):
        pass

    @classmethod
    def handle(cls, query):
        pass


class BaseList(BaseControl):
    @classmethod
    def create(cls, **kw_args):
        print("!!", kw_args)
        kw_args["offset"] = 0
        kw_args["num_items"] = len(kw_args["items"])
        if "menu_size" not in kw_args:
            kw_args["menu_size"] = 10
        return super().create(**kw_args)

    @classmethod
    def format_item(cls, item):
        return item["name"]

    @classmethod
    def build_message_attrs(cls, data):
        return {"text": cls.build_text(data), "reply_markup": cls.build_keyboard(data), "parse_mode": "Markdown"}

    @classmethod
    def build_text(cls, data):
        beg_r = data["offset"] + 1
        end_r = data["offset"] + data["menu_size"]
        total_r = data["num_items"]
        return f"{data['title']}\n({beg_r} - {end_r} из {total_r})"

    @classmethod
    def build_keyboard(cls, data):
        btns = []
        for i in range(data["menu_size"]):
            name = cls.format_item(data["items"][data["offset"] + i])
            btns.append([InlineKeyboardButton(name, callback_data=(data, i))])
        btns.append(cls.build_ctrl_buttons(data))
        return InlineKeyboardMarkup(btns)

    @classmethod
    def build_ctrl_buttons(cls, data):
        return [
            InlineKeyboardButton(emoji.emojize(":last_track_button:"), callback_data=(data, MENU_FIRST)),
            InlineKeyboardButton(emoji.emojize(":reverse_button:"), callback_data=(data, MENU_PREV)),
            InlineKeyboardButton(emoji.emojize(":play_button:"), callback_data=(data, MENU_NEXT)),
            InlineKeyboardButton(emoji.emojize(":next_track_button:"), callback_data=(data, MENU_LAST)),
            InlineKeyboardButton(emoji.emojize(":cross_mark:"), callback_data=(data, MENU_CLOSE)),
        ]

    @classmethod
    def handle(self, query):
        if not super().handle(query):
            data, button_id = query.data
            if button_id >= 0:
                return False
            elif button_id == MENU_CLOSE:
                query.delete_message()
            else:
                query.edit_message_text(**cls.build_message_attrs(data))
        return True


class TrackList(BaseList):
    sign = "TrackList"

    @classmethod
    def create(cls, **kw_args):
        if "search_str" in kw_args:
            kw_args["title"] = f"Поиск записей: *{kw_args['search_str']}*"
        if "user_id" in kw_args:
            kw_args["title"] = f"Избранные записи: *{kw_args['user_id']}*"
        return super().create(**kw_args)

    @classmethod
    def format_item(cls, item):
        return f"{item['name']} - {item['artist_name']}"

    @classmethod
    def handle(self, query):
        if super().handle(query):
            return True
        else:
            data, button_id = query.data
            if button_id >= 0:
                query.bot.send_message(query.message.chat_id, str(button_id))
                return True
        return False


class AlbumList(BaseList):
    sign = "AlbumList"

    @classmethod
    def create(cls, **kw_args):
        if "search_str" in kw_args:
            kw_args["title"] = f"*Поиск альбомов:* _{kw_args['search_str']}_"
        if "user_id" in kw_args:
            kw_args["title"] = f"Избранные альбомы: *{kw_args['user_id']}*"
        return super().create(**kw_args)

    @classmethod
    def format_item(cls, item):
        return ""


class ArtistList(BaseList):
    sign = "ArtistList"

    @classmethod
    def create(cls, **kw_args):
        if "search_str" in kw_args:
            kw_args["title"] = f"*Поиск исполнителей:* _{kw_args['search_str']}_"
        if "user_id" in kw_args:
            kw_args["title"] = f"Избранные исполнители: *{kw_args['user_id']}*"
        return super().create(**kw_args)

    @classmethod
    def format_item(cls, item):
        return ""


class ArtistAlbums(BaseList):
    pass


class AlbumTracks(BaseList):
    pass


for cls in (Track, TrackList, AlbumList, ArtistList, ArtistAlbums, AlbumTracks):
    sign2ctrl[cls.sign] = cls
