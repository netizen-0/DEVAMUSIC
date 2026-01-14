import asyncio
import importlib

from pyrogram import idle

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

    # Load sudo & banned users
    await sudo()
    try:
        for user_id in await get_gbanned():
            BANNED_USERS.add(user_id)
        for user_id in await get_banned_users():
            BANNED_USERS.add(user_id)
    except Exception as e:
        LOGGER(__name__).warning(f"Banned users load skipped: {e}")

    # Start main bot
    await app.start()

    # Load plugins
    for all_module in ALL_MODULES:
        importlib.import_module("VIP_INNOCENT.plugins" + all_module)

    LOGGER("VIP_INNOCENT.plugins").info(
        "𝐀𝐥𝐥 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬 𝐋𝐨𝐚𝐝𝐞𝐝 𝐁𝐚𝐛𝐲🥳..."
    )

    # Start assistant & VC
    await userbot.start()
    await INNOCENT.start()

    # VC warmup (SAFE: no pytgcalls exception import)
    try:
        await INNOCENT.stream_call(
            "https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4"
        )
    except Exception as e:
        LOGGER("VIP_INNOCENT").warning(
            f"VC warmup skipped (safe ignore): {e}"
        )

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
