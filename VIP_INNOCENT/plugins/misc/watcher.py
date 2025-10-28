from pyrogram import filters
from pyrogram.types import Message

from VIP_INNOCENT import app
from VIP_INNOCENT.core.call import INNOCENT

welcome = 20
close = 30


@app.on_message(filters.video_chat_started, group=welcome)
@app.on_message(filters.video_chat_ended, group=close)
async def welcome(_, message: Message):
    await INNOCENT.stop_stream_force(message.chat.id)
