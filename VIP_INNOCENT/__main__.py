import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import GroupCallNotFound

import config
from VIP_INNOCENT import LOGGER, app, userbot
from VIP_INNOCENT.core.call import INNOCENT
from VIP_INNOCENT.misc import sudo
from VIP_INNOCENT.plugins import ALL_MODULES
from VIP_INNOCENT.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS
from VIP_INNOCENT.plugins.tools.clone import restart_bots


async def init():
    if not config.STRING1:
        LOGGER(__name__).error(
            "String Session not filled, please provide a valid session."
        )
        return

    await sudo()

    # Load banned users
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)

        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except Exception as e:
        LOGGER(__name__).warning(f"Failed to load banned users: {e}")

    # Start bot clients
    await app.start()

    for all_module in ALL_MODULES:
        importlib.import_module("VIP_INNOCENT.plugins" + all_module)

    LOGGER("VIP_INNOCENT.plugins").info(
        "𝐀𝐥𝐥 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬 𝐋𝐨𝐚𝐝𝐞𝐝 𝐁𝐚𝐛𝐲🥳..."
    )

    await userbot.start()
    await INNOCENT.start()

    # Test VC connection (PyTgCalls v3 safe)
    try:
        await INNOCENT.stream_call(
            "https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4"
        )
    except GroupCallNotFound:
        LOGGER("VIP_INNOCENT").error(
            "𝗣𝗹𝗲𝗮𝘀𝗲 𝗦𝘁𝗮𝗿𝘁 𝗬𝗼𝘂𝗿 𝗟𝗼𝗴 𝗚𝗿𝗼𝘂𝗽 / 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝗩𝗼𝗶𝗰𝗲 𝗖𝗵𝗮𝘁\n\n"
            "𝗠𝘂𝘀𝗶𝗰 𝗕𝗼𝘁 𝗦𝘁𝗼𝗽𝗽𝗲𝗱 ❌"
        )
        return
    except Exception as e:
        LOGGER("VIP_INNOCENT").warning(f"VC warmup skipped: {e}")

    await INNOCENT.decorators()
    await restart_bots()

    LOGGER("VIP_INNOCENT").info(
        "╔═════ஜ۩۞۩ஜ════╗\n"
        "  ☠︎︎𝗠𝗔𝗗𝗘 𝗕𝗬 VERON 𝗕𝗼t𝘀☠︎︎\n"
        "╚═════ஜ۩۞۩ஜ════╝"
    )

    await idle()

    await app.stop()
    await userbot.stop()

    LOGGER("VIP_INNOCENT").info("𝗦𝗧𝗢𝗣 𝗠𝗨𝗦𝗜𝗖 🎻 𝗕𝗢𝗧..")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
