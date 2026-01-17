from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus, ParseMode

import config
from ..logging import LOGGER


def _normalize_logger_id(value):
    """
    Accepts:
      - int chat id (preferred)
      - "-100..." / "-123..." as string
      - "@username"
      - "https://t.me/username" / "t.me/username"
    Returns: int or str (@username)
    Raises: ValueError if invalid
    """
    if value is None:
        raise ValueError("LOGGER_ID is None")

    # if already int
    if isinstance(value, int):
        return value

    v = str(value).strip()
    if not v or v.lower() in {"none", "null"}:
        raise ValueError(f"LOGGER_ID is empty/invalid: {value!r}")

    # remove t.me links
    v = v.replace("https://t.me/", "").replace("http://t.me/", "").replace("t.me/", "").strip()

    # username
    if v.startswith("@"):
        if len(v) < 2:
            raise ValueError(f"LOGGER_ID username invalid: {value!r}")
        return v

    # numeric id
    if v.lstrip("-").isdigit():
        return int(v)

    # if someone provided plain username without @
    if v.isalnum() or "_" in v:
        return f"@{v}"

    raise ValueError(f"LOGGER_ID format invalid: {value!r}")


class INNOCENT(Client):
    def __init__(self):
        LOGGER(__name__).info("Starting Bot...")
        super().__init__(
            name="VIP_INNOCENT",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.username = self.me.username
        self.mention = self.me.mention

        # ✅ Normalize LOGGER_ID safely
        try:
            log_chat_id = _normalize_logger_id(getattr(config, "LOGGER_ID", None))
        except Exception as ex:
            LOGGER(__name__).warning(
                f"LOGGER_ID invalid. Logs will be disabled.\n  Reason : {type(ex).__name__}: {ex}"
            )
            log_chat_id = None

        # ✅ Try sending startup message, but DON'T crash bot if it fails
        if log_chat_id:
            try:
                await self.send_message(
                    chat_id=log_chat_id,
                    text=(
                        f"<u><b>» {self.mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ :</b></u>\n\n"
                        f"ɪᴅ : <code>{self.id}</code>\n"
                        f"ɴᴀᴍᴇ : {self.name}\n"
                        f"ᴜsᴇʀɴᴀᴍᴇ : @{self.username}"
                    ),
                    parse_mode=ParseMode.HTML,
                )
            except (errors.ChannelInvalid, errors.PeerIdInvalid, errors.ChatAdminRequired) as ex:
                LOGGER(__name__).warning(
                    "Bot couldn't access log group/channel. Logs will be disabled.\n"
                    f"  Reason : {type(ex).__name__}."
                )
                log_chat_id = None
            except Exception as ex:
                LOGGER(__name__).warning(
                    "Bot couldn't send startup log message. Logs will be disabled.\n"
                    f"  Reason : {type(ex).__name__}."
                )
                log_chat_id = None

        # ✅ Admin check only if log_chat_id is working
        if log_chat_id:
            try:
                a = await self.get_chat_member(log_chat_id, self.id)
                if a.status != ChatMemberStatus.ADMINISTRATOR:
                    LOGGER(__name__).warning(
                        "Bot is not admin in log group/channel. Logs may not work properly."
                    )
            except Exception as ex:
                LOGGER(__name__).warning(
                    f"Couldn't verify admin status in log chat. Reason: {type(ex).__name__}."
                )

        LOGGER(__name__).info(f"Music Bot Started as {self.name}")

    async def stop(self):
        await super().stop()
