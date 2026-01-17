import asyncio
import os
from random import randint
from typing import Dict, List, Union

import requests
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtube_search import YoutubeSearch

from config import BANNED_USERS, SERVER_PLAYLIST_LIMIT
from VIP_INNOCENT import Carbon, app
from VIP_INNOCENT.core.mongo import mongodb
from VIP_INNOCENT.utils.decorators.language import language, languageCB
from VIP_INNOCENT.utils.inline.playlist import (
    botplaylist_markup,
    get_playlist_markup,
    warning_markup,
)
from VIP_INNOCENT.utils.pastebin import INNOCENTBin
from VIP_INNOCENT.utils.stream.stream import stream

import time  # keep only this

playlistdb = mongodb.playlist

# Anti-spam
user_last_message_time = {}
user_command_count = {}
SPAM_THRESHOLD = 2
SPAM_WINDOW_SECONDS = 5


# ---------------- DB helpers ----------------
async def _get_playlists(chat_id: int) -> Dict[str, dict]:
    _notes = await playlistdb.find_one({"chat_id": chat_id})
    if not _notes:
        return {}
    return _notes.get("notes", {})


async def get_playlist_names(chat_id: int) -> List[str]:
    _notes = await _get_playlists(chat_id)
    return list(_notes.keys())


async def get_playlist(chat_id: int, name: str) -> Union[bool, dict]:
    _notes = await _get_playlists(chat_id)
    return _notes.get(name, False)


async def save_playlist(chat_id: int, name: str, note: dict):
    _notes = await _get_playlists(chat_id)
    _notes[name] = note
    await playlistdb.update_one(
        {"chat_id": chat_id}, {"$set": {"notes": _notes}}, upsert=True
    )


async def delete_playlist(chat_id: int, name: str) -> bool:
    notesd = await _get_playlists(chat_id)
    if name in notesd:
        del notesd[name]
        await playlistdb.update_one(
            {"chat_id": chat_id},
            {"$set": {"notes": notesd}},
            upsert=True,
        )
        return True
    return False


# Commands
ADDPLAYLIST_COMMAND = "addplaylist"
PLAYLIST_COMMAND = "playlist"
DELETEPLAYLIST_COMMAND = "delplaylist"
DELETE_ALL_PLAYLIST_COMMAND = "delallplaylist"


def _spam_check(message: Message) -> bool:
    user_id = message.from_user.id
    current_time = time.time()
    last_message_time = user_last_message_time.get(user_id, 0)

    if current_time - last_message_time < SPAM_WINDOW_SECONDS:
        user_last_message_time[user_id] = current_time
        user_command_count[user_id] = user_command_count.get(user_id, 0) + 1
        if user_command_count[user_id] > SPAM_THRESHOLD:
            return True
    else:
        user_command_count[user_id] = 1
        user_last_message_time[user_id] = current_time

    return False


# ---------------- playlist list ----------------
@app.on_message(filters.command(PLAYLIST_COMMAND) & ~BANNED_USERS)
@language
async def check_playlist(client, message: Message, _):
    if _spam_check(message):
        hu = await message.reply_text(
            f"**{message.from_user.mention} ᴘʟᴇᴀsᴇ ᴅᴏɴᴛ ᴅᴏ sᴘᴀᴍ, ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 5 sᴇᴄ**"
        )
        await asyncio.sleep(3)
        await hu.delete()
        return

    _playlist = await get_playlist_names(message.from_user.id)
    if _playlist:
        get = await message.reply_text(_["playlist_2"])
    else:
        return await message.reply_text(_["playlist_3"])

    msg = _["playlist_4"]
    count = 0
    for vid in _playlist:
        _note = await get_playlist(message.from_user.id, vid)
        title = (_note.get("title") or "Unknown").title()
        duration = _note.get("duration", 0)
        count += 1
        msg += f"\n\n{count}- {title[:70]}\n"
        msg += _["playlist_5"].format(duration)

    link = await INNOCENTBin(msg)

    lines = msg.count("\n")
    if lines >= 17:
        car = os.linesep.join(msg.split(os.linesep)[:17])
    else:
        car = msg

    carbon = await Carbon.generate(car, randint(100, 10000000000))
    await get.delete()
    await message.reply_photo(carbon, caption=_["playlist_15"].format(link))


# ✅ FIXED keyboard builder (NO pykeyboard)
async def get_keyboard(_, user_id: int):
    buttons = []
    _playlist = await get_playlist_names(user_id)
    count = len(_playlist)

    for x in _playlist:
        _note = await get_playlist(user_id, x)
        title = (_note.get("title") or "Unknown").title()
        buttons.append(
            [InlineKeyboardButton(text=title[:60], callback_data=f"del_playlist {x}")]
        )

    buttons.append(
        [
            InlineKeyboardButton(text=_["PL_B_5"], callback_data="delete_warning"),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
        ]
    )

    return InlineKeyboardMarkup(buttons), count


# ---------------- delete playlist UI ----------------
@app.on_message(filters.command(DELETEPLAYLIST_COMMAND) & ~BANNED_USERS)
@language
async def del_plist_msg(client, message: Message, _):
    if _spam_check(message):
        hu = await message.reply_text(
            f"**{message.from_user.mention} ᴘʟᴇᴀsᴇ ᴅᴏɴᴛ ᴅᴏ sᴘᴀᴍ, ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 5 sᴇᴄ**"
        )
        await asyncio.sleep(3)
        await hu.delete()
        return

    _playlist = await get_playlist_names(message.from_user.id)
    if _playlist:
        get = await message.reply_text(_["playlist_2"])
    else:
        return await message.reply_text(_["playlist_3"])

    keyboard, count = await get_keyboard(_, message.from_user.id)
    await get.edit_text(_["playlist_7"].format(count), reply_markup=keyboard)


# ---------------- play playlist ----------------
@app.on_callback_query(filters.regex("^play_playlist") & ~BANNED_USERS)
@languageCB
async def play_playlist_cb(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    mode = callback_data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id

    _playlist = await get_playlist_names(user_id)
    if not _playlist:
        try:
            return await CallbackQuery.answer(_["playlist_3"], show_alert=True)
        except:
            return

    chat_id = CallbackQuery.message.chat.id
    user_name = CallbackQuery.from_user.first_name

    try:
        await CallbackQuery.answer()
    except:
        pass

    await CallbackQuery.message.delete()

    result = list(_playlist)
    video = True if mode == "v" else None
    mystic = await CallbackQuery.message.reply_text(_["play_1"])

    try:
        await stream(
            _,
            mystic,
            user_id,
            result,
            chat_id,
            user_name,
            chat_id,
            video,
            streamtype="playlist",
        )
    except Exception as e:
        ex_type = type(e).__name__
        err = e if ex_type == "AssistantErr" else _["general_3"].format(ex_type)
        return await mystic.edit_text(err)

    return await mystic.delete()


@app.on_message(
    filters.command(["playplaylist", "vplayplaylist"]) & ~BANNED_USERS & filters.group
)
@languageCB
async def play_playlist_command(client, message: Message, _):
    mode = message.command[0][0]
    user_id = message.from_user.id

    _playlist = await get_playlist_names(user_id)
    if not _playlist:
        try:
            return await message.reply(_["playlist_3"], quote=True)
        except:
            return

    chat_id = message.chat.id
    user_name = message.from_user.first_name

    try:
        await message.delete()
    except:
        pass

    result = list(_playlist)
    video = True if mode == "v" else None
    mystic = await message.reply_text(_["play_1"])

    try:
        await stream(
            _,
            mystic,
            user_id,
            result,
            chat_id,
            user_name,
            chat_id,
            video,
            streamtype="playlist",
        )
    except Exception as e:
        ex_type = type(e).__name__
        err = e if ex_type == "AssistantErr" else _["general_3"].format(ex_type)
        return await mystic.edit_text(err)

    return await mystic.delete()


# ---------------- add playlist ----------------
@app.on_message(filters.command(ADDPLAYLIST_COMMAND) & ~BANNED_USERS)
@language
async def add_playlist_cmd(client, message: Message, _):
    if len(message.command) < 2:
        return await message.reply_text(
            "**➻ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴍᴇ ᴀ sᴏɴɢ ɴᴀᴍᴇ ᴏʀ sᴏɴɢ ʟɪɴᴋ ᴏʀ ʏᴏᴜᴛᴜʙᴇ ᴘʟᴀʏʟɪsᴛ ʟɪɴᴋ ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ..**\n\n"
            "**➥ ᴇxᴀᴍᴘʟᴇs:**\n\n"
            "▷ `/addplaylist Blue Eyes`\n\n"
            "▷ `/addplaylist [youtube playlist link]`"
        )

    query = " ".join(message.command[1:]).strip()

    # YouTube Playlist link
    if "youtube.com/playlist" in query:
        adding = await message.reply_text("**🎧 ᴀᴅᴅɪɴɢ sᴏɴɢs ɪɴ ᴘʟᴀʏʟɪsᴛ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..**")
        try:
            from pytube import Playlist, YouTube

            pl = Playlist(query)
            video_urls = pl.video_urls
        except Exception as e:
            await adding.delete()
            return await message.reply_text(f"Error: {e}")

        if not video_urls:
            await adding.delete()
            return await message.reply_text("**➻ ɴᴏ sᴏɴɢs ғᴏᴜɴᴅ ɪɴ ᴛʜᴇ ᴘʟᴀʏʟɪsᴛ ʟɪɴᴋ.**")

        user_id = message.from_user.id
        added_count = 0

        for video_url in video_urls:
            video_id = video_url.split("v=")[-1].split("&")[0]
            if await get_playlist(user_id, video_id):
                continue

            try:
                yt = YouTube(video_url)
                title = yt.title
                duration = yt.length
            except:
                continue

            plist = {"videoid": video_id, "title": title, "duration": duration}
            await save_playlist(user_id, video_id, plist)
            added_count += 1

            if len(await get_playlist_names(user_id)) >= SERVER_PLAYLIST_LIMIT:
                break

        keyboardes = InlineKeyboardMarkup(
            [[InlineKeyboardButton("๏ ᴡᴀɴᴛ ʀᴇᴍᴏᴠᴇ ᴀɴʏ sᴏɴɢs? ๏", callback_data=f"open_playlist {user_id}")]]
        )
        await adding.delete()
        return await message.reply_text(
            text=f"**➻ {added_count} sᴏɴɢ(s) ᴀᴅᴅᴇᴅ ✅**\n\n**▷ ᴄʜᴇᴄᴋ ʙʏ » /playlist**",
            reply_markup=keyboardes,
        )

    # YouTube channel (@username) block was broken in your code (undefined functions)
    if "youtube.com/@" in query:
        return await message.reply_text(
            "**➻ YouTube channel (@username) add feature abhi disabled hai (code me function missing tha).**\n\n"
            "**➥ Please use:**\n"
            "▷ `/addplaylist song name`\n"
            "▷ `/addplaylist https://youtu.be/VIDEO_ID`\n"
            "▷ `/addplaylist youtube playlist link`"
        )

    # youtu.be single video link
    if "youtu.be/" in query:
        add = await message.reply_text("**🎧 ᴀᴅᴅɪɴɢ sᴏɴɢ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..**")
        try:
            from pytube import YouTube

            videoid = query.split("youtu.be/")[-1].split("?")[0].split("&")[0]
            user_id = message.from_user.id

            thumbnail = f"https://img.youtube.com/vi/{videoid}/maxresdefault.jpg"
            if await get_playlist(user_id, videoid):
                await add.delete()
                return await message.reply_photo(thumbnail, caption=_["playlist_8"])

            if len(await get_playlist_names(user_id)) >= SERVER_PLAYLIST_LIMIT:
                await add.delete()
                return await message.reply_text(_["playlist_9"].format(SERVER_PLAYLIST_LIMIT))

            yt = YouTube(f"https://youtu.be/{videoid}")
            title = yt.title
            duration = yt.length

            plist = {"videoid": videoid, "title": title, "duration": duration}
            await save_playlist(user_id, videoid, plist)

            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("๏ Remove from Playlist ๏", callback_data=f"remove_playlist {videoid}")]]
            )

            await add.delete()
            return await message.reply_photo(
                thumbnail,
                caption="**➻ ᴀᴅᴅᴇᴅ sᴏɴɢ ✅**\n\n**➥ /playlist | /delplaylist**",
                reply_markup=keyboard,
            )
        except Exception as e:
            await add.delete()
            return await message.reply_text(str(e))

    # song name search
    from VIP_INNOCENT import YouTube

    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        thumbnail = results[0]["thumbnails"][0]
        videoid = results[0]["id"]

        user_id = message.from_user.id
        if await get_playlist(user_id, videoid):
            return await message.reply_photo(thumbnail, caption=_["playlist_8"])

        if len(await get_playlist_names(user_id)) >= SERVER_PLAYLIST_LIMIT:
            return await message.reply_text(_["playlist_9"].format(SERVER_PLAYLIST_LIMIT))

        m = await message.reply("**🔄 ᴀᴅᴅɪɴɢ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...**")
        title, duration_min, _, _, _ = await YouTube.details(videoid, True)
        title = (title[:50]).title()

        plist = {"videoid": videoid, "title": title, "duration": duration_min}
        await save_playlist(user_id, videoid, plist)

        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("๏ Remove from Playlist ๏", callback_data=f"remove_playlist {videoid}")]]
        )

        await m.delete()
        return await message.reply_photo(
            thumbnail,
            caption="**➻ ᴀᴅᴅᴇᴅ ✅**\n\n**➥ /playlist | /delplaylist**",
            reply_markup=keyboard,
        )
    except Exception:
        return await message.reply_text("**➻ Song nahi mila. Try another query.**")


# ---------------- callbacks ----------------
@app.on_callback_query(filters.regex("^open_playlist") & ~BANNED_USERS)
@languageCB
async def open_playlist_cb(client, CallbackQuery, _):
    _playlist = await get_playlist_names(CallbackQuery.from_user.id)
    if not _playlist:
        return await CallbackQuery.message.edit_text(_["playlist_3"])

    keyboard, count = await get_keyboard(_, CallbackQuery.from_user.id)
    return await CallbackQuery.message.edit_text(_["playlist_7"].format(count), reply_markup=keyboard)


@app.on_callback_query(filters.regex("^remove_playlist") & ~BANNED_USERS)
@languageCB
async def remove_playlist_cb(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]

    deleted = await delete_playlist(CallbackQuery.from_user.id, videoid)
    if deleted:
        try:
            await CallbackQuery.answer(_["playlist_11"], show_alert=True)
        except:
            pass
    else:
        try:
            return await CallbackQuery.answer(_["playlist_12"], show_alert=True)
        except:
            return

    keyboards = InlineKeyboardMarkup(
        [[InlineKeyboardButton("๏ ʀᴇᴄᴏᴠᴇʀ ʏᴏᴜʀ sᴏɴɢ ๏", callback_data=f"recover_playlist {videoid}")]]
    )
    return await CallbackQuery.edit_message_text(
        text="**➻ Deleted from playlist.**\n\n**➥ Recover karna ho to button dabao.**",
        reply_markup=keyboards,
    )


@app.on_callback_query(filters.regex("^recover_playlist") & ~BANNED_USERS)
@languageCB
async def recover_playlist_cb(client, CallbackQuery, _):
    from VIP_INNOCENT import YouTube

    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id

    if await get_playlist(user_id, videoid):
        try:
            return await CallbackQuery.answer(_["playlist_8"], show_alert=True)
        except:
            return

    if len(await get_playlist_names(user_id)) >= SERVER_PLAYLIST_LIMIT:
        try:
            return await CallbackQuery.answer(
                _["playlist_9"].format(SERVER_PLAYLIST_LIMIT), show_alert=True
            )
        except:
            return

    title, duration_min, _, _, vidid = await YouTube.details(videoid, True)
    title = (title[:50]).title()

    plist = {"videoid": vidid, "title": title, "duration": duration_min}
    await save_playlist(user_id, videoid, plist)

    keyboardss = InlineKeyboardMarkup(
        [[InlineKeyboardButton("๏ ʀᴇᴍᴏᴠᴇ ᴀɢᴀɪɴ ๏", callback_data=f"remove_playlist {videoid}")]]
    )
    return await CallbackQuery.edit_message_text(
        text="**➻ Recovered ✅**\n\n**➥ /playlist**",
        reply_markup=keyboardss,
    )


@app.on_callback_query(filters.regex("^add_playlist$") & ~BANNED_USERS)
@languageCB
async def add_playlist_help_cb(client, CallbackQuery, _):
    await CallbackQuery.answer(
        "➻ Add song: /addplaylist songname\n➥ Example: /addplaylist Blue Eyes",
        show_alert=True,
    )


@app.on_message(filters.command(DELETE_ALL_PLAYLIST_COMMAND) & ~BANNED_USERS)
@language
async def delete_all_playlists_cmd(client, message: Message, _):
    user_id = message.from_user.id
    _playlist = await get_playlist_names(user_id)
    if _playlist:
        upl = warning_markup(_)
        return await message.reply_text(_["playlist_14"], reply_markup=upl)
    return await message.reply_text(_["playlist_3"])


@app.on_callback_query(filters.regex("^del_playlist") & ~BANNED_USERS)
@languageCB
async def del_one_from_list_cb(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id

    deleted = await delete_playlist(user_id, videoid)
    if deleted:
        try:
            await CallbackQuery.answer(_["playlist_11"], show_alert=True)
        except:
            pass
    else:
        try:
            return await CallbackQuery.answer(_["playlist_12"], show_alert=True)
        except:
            return

    keyboard, count = await get_keyboard(_, user_id)
    return await CallbackQuery.edit_message_reply_markup(reply_markup=keyboard)


@app.on_callback_query(filters.regex("^delete_whole_playlist$") & ~BANNED_USERS)
@languageCB
async def del_whole_playlist_cb(client, CallbackQuery, _):
    _playlist = await get_playlist_names(CallbackQuery.from_user.id)
    try:
        await CallbackQuery.answer("Deleting playlist...", show_alert=True)
    except:
        pass

    for x in _playlist:
        await delete_playlist(CallbackQuery.from_user.id, x)

    return await CallbackQuery.edit_message_text(_["playlist_13"])


@app.on_callback_query(filters.regex("^get_playlist_playmode$") & ~BANNED_USERS)
@languageCB
async def get_playlist_playmode_cb(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except:
        pass
    buttons = get_playlist_markup(_)
    return await CallbackQuery.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))


@app.on_callback_query(filters.regex("^delete_warning$") & ~BANNED_USERS)
@languageCB
async def delete_warning_message_cb(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except:
        pass
    upl = warning_markup(_)
    return await CallbackQuery.edit_message_text(_["playlist_14"], reply_markup=upl)


@app.on_callback_query(filters.regex("^home_play$") & ~BANNED_USERS)
@languageCB
async def home_play_cb(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except:
        pass
    buttons = botplaylist_markup(_)
    return await CallbackQuery.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))


@app.on_callback_query(filters.regex("^del_back_playlist$") & ~BANNED_USERS)
@languageCB
async def del_back_playlist_cb(client, CallbackQuery, _):
    user_id = CallbackQuery.from_user.id
    _playlist = await get_playlist_names(user_id)

    if not _playlist:
        try:
            return await CallbackQuery.answer(_["playlist_3"], show_alert=True)
        except:
            return

    keyboard, count = await get_keyboard(_, user_id)
    return await CallbackQuery.edit_message_text(_["playlist_7"].format(count), reply_markup=keyboard)
