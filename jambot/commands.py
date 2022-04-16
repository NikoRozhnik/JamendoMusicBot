import emoji
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from .commons import commons


MENU_FIRST = -1
MENU_PREV = -2
MENU_NEXT = -3
MENU_LAST = -4
MENU_CLOSE = -5
NAV_BUTTONS = (MENU_FIRST, MENU_PREV, MENU_NEXT, MENU_LAST, MENU_CLOSE)


FIND_TRACKS_TEMPLATE = "*Поиск записей:* _{}_\n({} - {} из {})"


def create_menu(items, head_str, menu_items=10):
    return {"items": items, "offset": 0, "number": len(items), "menu_items": menu_items, "head_str": head_str}


def build_ctrl_buttons(menu):
    return [
        InlineKeyboardButton(emoji.emojize(":last_track_button:"), callback_data=(menu, MENU_FIRST)),
        InlineKeyboardButton(emoji.emojize(":reverse_button:"), callback_data=(menu, MENU_PREV)),
        InlineKeyboardButton(emoji.emojize(":play_button:"), callback_data=(menu, MENU_NEXT)),
        InlineKeyboardButton(emoji.emojize(":next_track_button:"), callback_data=(menu, MENU_LAST)),
        InlineKeyboardButton(emoji.emojize(":cross_mark:"), callback_data=(menu, MENU_CLOSE)),
    ]


def build_keyboard(menu, button_id=None):
    btns = []
    for i in range(menu["menu_items"]):
        name = menu["items"][menu["offset"] + i]["name"]
        btns.append([InlineKeyboardButton(name, callback_data=(menu, i))])
    btns.append(build_ctrl_buttons(menu))
    return InlineKeyboardMarkup(btns)


def handle_button(update, context):
    query = update.callback_query
    query.answer()
    menu, button_id = query.data
    print("button_id:", button_id)
    if button_id >= 0:
        # print(dir(context.bot))
        query.bot.send_message(query.message.chat_id, str(button_id))
        pass
    elif button_id == MENU_CLOSE:
        query.delete_message()
    else:
        beg_r = 0
        end_r = 10
        total_r = 100
        query.edit_message_text(
            text=FIND_TRACKS_TEMPLATE.format(menu["head_str"], beg_r, end_r, total_r),
            reply_markup=build_keyboard(menu, button_id),
            parse_mode="Markdown",
        )


def find_artists(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="find_artists")


def find_albums(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="find_albums")


def find_tracks(update, context):
    head_str = " ".join(context.args)
    tracks = commons.jamAPI.search_tracks(context.args)
    menu = create_menu(tracks, head_str)
    beg_r = menu["offset"] + 1
    end_r = menu["offset"] + menu["menu_items"]
    total_r = menu["number"]
    update.message.reply_text(
        text=FIND_TRACKS_TEMPLATE.format(head_str, beg_r, end_r, total_r),
        reply_markup=build_keyboard(menu, None),
        parse_mode="Markdown",
    )


def fav_artists(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="artists")


def fav_albums(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="albums")


def fav_tracks(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="tracks")
