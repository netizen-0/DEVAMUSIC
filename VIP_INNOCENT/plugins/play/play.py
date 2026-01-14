import random
import string

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, Message
from pytgcalls.exceptions import NoActiveGroupCall

import config
from VIP_INNOCENT import Apple, Resso, SoundCloud, Spotify, Telegram, YouTube, app, LOGGER
from VIP_INNOCENT.core.call import INNOCENT
from VIP_INNOCENT.utils import seconds_to_min, time_to_seconds
from VIP_INNOCENT.utils.channelplay import get_channeplayCB
from VIP_INNOCENT.utils.decorators.language import languageCB
from VIP_INNOCENT.utils.decorators.play import PlayWrapper
from VIP_INNOCENT.utils.formatters import formats
from VIP_INNOCENT.utils.inline import (
    botplaylist_markup,
    livestream_markup,
    playlist_markup,
    slider_markup,
    track_markup,
)
from VIP_INNOCENT.utils.logger import play_logs
from VIP_INNOCENT.utils.stream.stream import stream
from config import BANNED_USERS, lyrical


# ===============================
# PLAY COMMAND
# ===============================

@app.on_message(
    filters.command(
        [
            "play", "vplay", "cplay", "cvplay",
            "playforce", "vplayforce", "cplayforce", "cvplayforce"
        ],
        prefixes=["/", "!", "%", ",", "", ".", "@", "#"],
    )
    & filters.group
    & ~BANNED_USERS
)
@PlayWrapper
async def play_commnd(
    client,
    message: Message,
    _,
    chat_id,
    video,
    channel,
    playmode,
    url,
    fplay,
):
    mystic = await message.reply_text(
        _["play_2"].format(channel) if channel else _["play_1"]
    )

    user_id = message.from_user.id
    user_name = message.from_user.first_name

    # ===============================
    # TELEGRAM AUDIO
    # ===============================
    audio_telegram = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )

    if audio_telegram:
        if audio_telegram.file_size > 104857600:
            return await mystic.edit_text(_["play_5"])

        if audio_telegram.duration > config.DURATION_LIMIT:
            return await mystic.edit_text(
                _["play_6"].format(config.DURATION_LIMIT_MIN, app.mention)
            )

        file_path = await Telegram.get_filepath(audio=audio_telegram)

        if not file_path:
            return await mystic.edit_text("❌ Failed to get audio file.")

        if await Telegram.download(_, message, mystic, file_path):
            details = {
                "title": await Telegram.get_filename(audio_telegram, audio=True),
                "link": await Telegram.get_link(message),
                "path": file_path,
                "dur": await Telegram.get_duration(audio_telegram, file_path),
            }

            result = await stream(
                _,
                mystic,
                user_id,
                details,
                chat_id,
                user_name,
                message.chat.id,
                streamtype="telegram",
                forceplay=fplay,
            )

            if not result:
                return await mystic.edit_text("❌ Failed to stream this file.")

            await mystic.delete()
            return await play_logs(message, streamtype="Telegram")

        return

    # ===============================
    # URL / YOUTUBE / SPOTIFY
    # ===============================
    if url:
        try:
            details, track_id = await YouTube.track(url)
        except Exception:
            return await mystic.edit_text(_["play_3"])

        if details.get("duration_min"):
            duration_sec = time_to_seconds(details["duration_min"])
            if duration_sec > config.DURATION_LIMIT:
                return await mystic.edit_text(
                    _["play_6"].format(config.DURATION_LIMIT_MIN, app.mention)
                )

        result = await stream(
            _,
            mystic,
            user_id,
            details,
            chat_id,
            user_name,
            message.chat.id,
            video=video,
            streamtype="youtube",
            forceplay=fplay,
        )

        if not result:
            return await mystic.edit_text("❌ Failed to start stream.")

        await mystic.delete()
        return await play_logs(message, streamtype="YouTube")

    # ===============================
    # NO QUERY
    # ===============================
    if len(message.command) < 2:
        return await mystic.edit_text(
            _["play_18"],
            reply_markup=InlineKeyboardMarkup(botplaylist_markup(_)),
        )


# ===============================
# CALLBACK PLAY
# ===============================

@app.on_callback_query(filters.regex("MusicStream") & ~BANNED_USERS)
@languageCB
async def play_music(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.split(None, 1)[1]
    vidid, user_id, mode, cplay, fplay = callback_data.split("|")

    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(_["playcb_1"], show_alert=True)

    chat_id, channel = await get_channeplayCB(_, cplay, CallbackQuery)
    mystic = await CallbackQuery.message.reply_text(
        _["play_2"].format(channel) if channel else _["play_1"]
    )

    try:
        details, track_id = await YouTube.track(vidid, True)
    except Exception:
        return await mystic.edit_text(_["play_3"])

    result = await stream(
        _,
        mystic,
        CallbackQuery.from_user.id,
        details,
        chat_id,
        CallbackQuery.from_user.first_name,
        CallbackQuery.message.chat.id,
        video=(mode == "v"),
        streamtype="youtube",
        forceplay=(fplay == "f"),
    )

    if not result:
        return await mystic.edit_text("❌ Failed to start stream.")

    await mystic.delete()
