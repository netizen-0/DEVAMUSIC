import time
import random
import asyncio

from pyrogram import filters, Client
from pyrogram.enums import ChatType
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    InputMediaPhoto,
)
from pyrogram.errors import RPCError

from youtubesearchpython.__future__ import VideosSearch

from VIP_INNOCENT import app
import config

from VIP_INNOCENT.misc import _boot_
from VIP_INNOCENT.plugins.sudo.sudoers import sudoers_list
from VIP_INNOCENT.utils.database import (
    get_served_chats,
    get_served_users,
    get_sudoers,
    add_served_chat_clone,
    add_served_user_clone,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from VIP_INNOCENT.utils import bot_sys_stats
from VIP_INNOCENT.utils.decorators.language import LanguageStart
from VIP_INNOCENT.utils.formatters import get_readable_time
from VIP_INNOCENT.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS, OWNER_ID, STREAMI_PICS
from strings import get_string

from VIP_INNOCENT.utils.database.clonedb import (
    get_owner_id_from_db,
    get_cloned_support_chat,
    get_cloned_support_channel,
)

from VIP_INNOCENT.cplugin.setinfo import get_logging_status, get_log_channel


# ================================
# START COMMAND (PRIVATE)
# ================================

@Client.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    a = await client.get_me()
    bot_id = a.id

    await add_served_user_clone(message.from_user.id, bot_id)

    loading = await message.reply_text("⚡")
    await loading.edit_text("<b>sᴛᴀʀᴛɪɴɢ✨</b>")
    await asyncio.sleep(0.2)
    await loading.edit_text("<b>sᴛᴀʀᴛɪɴɢ✨...</b>")
    await asyncio.sleep(0.2)
    await loading.delete()

    C_BOT_OWNER_ID = get_owner_id_from_db(bot_id)

    C_BOT_SUPPORT_CHAT = await get_cloned_support_chat(bot_id)
    C_SUPPORT_CHAT = f"https://t.me/{C_BOT_SUPPORT_CHAT}"

    C_BOT_SUPPORT_CHANNEL = await get_cloned_support_channel(bot_id)
    C_SUPPORT_CHANNEL = f"https://t.me/{C_BOT_SUPPORT_CHANNEL}"

    # ================================
    # START WITH ARGUMENTS
    # ================================
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        if name.startswith("help"):
            keyboard = help_pannel(_)
            return await message.reply_photo(
                random.choice(STREAMI_PICS),
                caption=_["help_1"].format(C_SUPPORT_CHAT),
                reply_markup=keyboard,
            )

        if name.startswith("sud"):
            return await sudoers_list(client=client, message=message, _=_)

        if name.startswith("inf"):
            m = await message.reply_text("🔎")
            query = name.replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"

            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]

            searched_text = _["start_6"].format(
                title,
                duration,
                views,
                published,
                channellink,
                channel,
                a.mention,
            )

            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=_["S_B_8"], url=link),
                        InlineKeyboardButton(text=_["S_B_9"], url=C_SUPPORT_CHAT),
                    ],
                ]
            )

            await m.delete()
            return await client.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=key,
            )

    # ================================
    # NORMAL START
    # ================================

    out = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{a.username}?startgroup=true",
            )
        ],
        [
            # ✅ FIXED OWNER BUTTON (NO user_id)
            InlineKeyboardButton(
                text="ᴏᴡɴᴇʀ",
                url=f"tg://user?id={C_BOT_OWNER_ID}",
            ),
            InlineKeyboardButton(
                text="✦ υρ∂αтєѕ ✦",
                url=C_SUPPORT_CHANNEL,
            ),
        ],
        [
            InlineKeyboardButton(
                text="🍁 нєℓρ αи∂ ¢σммαи∂ѕ 🍁",
                callback_data="settings_back_helper",
            ),
        ],
    ]

    app_name = app.name
    app_link = f"https://t.me/{app.username}"

    try:
        await message.reply_photo(
            random.choice(STREAMI_PICS),
            caption=_["c_start_2"].format(
                message.from_user.mention,
                a.mention,
                app_name,
                app_link,
                app_name,
                app_link,
                C_SUPPORT_CHANNEL,
                C_SUPPORT_CHAT,
            ),
            reply_markup=InlineKeyboardMarkup(out),
        )
    except RPCError as e:
        print(f"[START ERROR] {e}")

    # ================================
    # LOGGING
    # ================================
    C_LOG_STATUS = get_logging_status(bot_id)
    C_LOGGER_ID = get_log_channel(bot_id)

    if C_LOG_STATUS:
        if str(C_LOGGER_ID) == "-100":
            C_LOGGER_ID = C_BOT_OWNER_ID

        try:
            await client.send_message(
                chat_id=int(C_LOGGER_ID),
                text=(
                    f"✦ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n"
                    f"✦ <b>ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>\n"
                    f"✦ <b>ᴜsᴇʀɴᴀᴍᴇ ➠</b> @{message.from_user.username}"
                ),
            )
        except Exception as e:
            print(f"[LOG ERROR] {e}")


# ================================
# START COMMAND (GROUP)
# ================================

@Client.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    a = await client.get_me()
    bot_id = a.id

    C_BOT_SUPPORT_CHAT = await get_cloned_support_chat(bot_id)
    C_SUPPORT_CHAT = f"https://t.me/{C_BOT_SUPPORT_CHAT}"

    C_BOT_SUPPORT_CHANNEL = await get_cloned_support_channel(bot_id)
    C_SUPPORT_CHANNEL = f"https://t.me/{C_BOT_SUPPORT_CHANNEL}"

    out = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"],
                url=f"https://t.me/{a.username}?startgroup=true",
            ),
            InlineKeyboardButton(text=_["S_B_2"], url=C_SUPPORT_CHAT),
        ],
    ]

    uptime = int(time.time() - _boot_)

    await message.reply_photo(
        random.choice(STREAMI_PICS),
        caption=_["start_1"].format(
            a.mention,
            get_readable_time(uptime),
        ),
        reply_markup=InlineKeyboardMarkup(out),
    )

    return await add_served_chat_clone(message.chat.id, bot_id)
