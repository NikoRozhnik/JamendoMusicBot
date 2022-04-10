def find_artists(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="find_artists")


def find_albums(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="find_albums")


def find_tracks(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="find_tracks")


def artists(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="artists")


def albums(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="albums")


def tracks(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="tracks")
