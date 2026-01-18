import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup

# ✅ Import based on pytgcalls version
try:
    from pytgcalls import PyTgCalls as TgCalls
except ImportError:
    try:
        from pytgcalls import Client as TgCalls
    except ImportError:
        from pytgcalls.client import Client as TgCalls

from pytgcalls.types import Update, AudioPiped, AudioVideoPiped, StreamAudioEnded
from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo

# ✅ SAFE pytgcalls exception import (works for all versions)
try:
    from pytgcalls.exceptions import PyTgCallsException as PyTgCallsError
except Exception:
    try:
        from pytgcalls.exceptions import PyTgCallsError
    except Exception:
        PyTgCallsError = Exception

import config
from VIP_INNOCENT import LOGGER, YouTube, app
from VIP_INNOCENT.misc import db
from VIP_INNOCENT.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from VIP_INNOCENT.utils.exceptions import AssistantErr
from VIP_INNOCENT.utils.formatters import (
    check_duration,
    seconds_to_min,
    speed_converter,
)
from VIP_INNOCENT.utils.inline.play import stream_markup, telegram_markup
from VIP_INNOCENT.utils.stream.autoclear import auto_clean
from strings import get_string
from VIP_INNOCENT.utils.thumbnails import get_thumb

autoend = {}
counter = {}


async def _clear_(chat_id):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)


class Call:
    def __init__(self):
        self.userbot1 = Client(
            name="VIP_INNOCENTAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        self.one = TgCalls(self.userbot1, cache_duration=150)

    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.pause_stream(chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.resume_stream(chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_group_call(chat_id)
        except:
            pass

    async def stop_stream_force(self, chat_id: int):
        try:
            if config.STRING1:
                await self.one.leave_group_call(chat_id)
        except:
            pass
        try:
            await _clear_(chat_id)
        except:
            pass

    async def skip_stream(self, chat_id: int, link, video=False):
        assistant = await group_assistant(self, chat_id)
        stream = (
            AudioVideoPiped(
                link,
                audio_parameters=HighQualityAudio(),
                video_parameters=MediumQualityVideo(),
            )
            if video
            else AudioPiped(link, audio_parameters=HighQualityAudio())
        )
        await assistant.change_stream(chat_id, stream)

    async def join_call(
        self,
        chat_id: int,
        original_chat_id: int,
        link,
        video: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)
        language = await get_lang(chat_id)
        _ = get_string(language)

        stream = (
            AudioVideoPiped(
                link,
                audio_parameters=HighQualityAudio(),
                video_parameters=MediumQualityVideo(),
            )
            if video
            else AudioPiped(link, audio_parameters=HighQualityAudio())
        )

        try:
            await assistant.join_group_call(chat_id, stream)
        except PyTgCallsError:
            raise AssistantErr(_["call_10"])

        await add_active_chat(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)

        if await is_autoend():
            users = len(await assistant.get_participants(chat_id))
            if users == 1:
                autoend[chat_id] = datetime.now() + timedelta(minutes=1)

    async def change_stream(self, client, chat_id):
        check = db.get(chat_id)
        try:
            popped = check.pop(0)
            await auto_clean(popped)
        except:
            await _clear_(chat_id)
            return await client.leave_group_call(chat_id)

        if not check:
            await _clear_(chat_id)
            return await client.leave_group_call(chat_id)

        queued = check[0]["file"]
        streamtype = check[0]["streamtype"]
        video = streamtype == "video"

        stream = (
            AudioVideoPiped(
                queued,
                audio_parameters=HighQualityAudio(),
                video_parameters=MediumQualityVideo(),
            )
            if video
            else AudioPiped(queued, audio_parameters=HighQualityAudio())
        )
        await client.change_stream(chat_id, stream)

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Client...")
        if config.STRING1:
            await self.one.start()

    async def decorators(self):
        @self.one.on_stream_end()
        async def stream_end_handler(client, update: Update):
            if isinstance(update, StreamAudioEnded):
                await self.change_stream(client, update.chat_id)


INNOCENT = Call()
