import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()


# ----------------------------
# Helpers (safe env parsing)
# ----------------------------
def _env(key: str, default=None):
    val = getenv(key, default)
    if isinstance(val, str):
        val = val.strip()
    return val


def _to_int(val, default=None):
    if val is None:
        return default
    try:
        return int(str(val).strip())
    except Exception:
        return default


def _to_bool(val, default=False):
    if val is None:
        return default
    v = str(val).strip().lower()
    if v in {"1", "true", "yes", "y", "on"}:
        return True
    if v in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _parse_logger_id(val):
    """
    Accept:
      - int chat id: -100xxxx / -xxxx
      - "@username"
      - "username"
      - "https://t.me/username" / "t.me/username"
    Return:
      int or "@username" or None
    """
    if val is None:
        return None
    v = str(val).strip()
    if not v or v.lower() in {"none", "null"}:
        return None

    v = v.replace("https://t.me/", "").replace("http://t.me/", "").replace("t.me/", "").strip()

    if v.startswith("@"):
        return v if len(v) > 1 else None

    if v.lstrip("-").isdigit():
        return int(v)

    # plain username
    if re.fullmatch(r"[A-Za-z0-9_]{5,}", v):
        return f"@{v}"

    return None


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


# ----------------------------
# Required / Core
# ----------------------------
API_ID = _to_int(_env("API_ID"))
API_HASH = _env("API_HASH")
BOT_TOKEN = _env("BOT_TOKEN")

# Optional IDs (safe)
BOT_ID = _env("BOT_ID")  # some repos use string here, leaving as-is
OWNER_ID = _to_int(_env("OWNER_ID", 7538572906), 7538572906)

# Bot Identity
OWNER_USERNAME = _env("OWNER_USERNAME", "btw_deva")
BOT_USERNAME = _env("BOT_USERNAME", "DEVA_MUSICBOT")
BOT_NAME = _env("BOT_NAME", "DEVA MUSIC")
ASSUSERNAME = _env("ASSUSERNAME", "Mus_ic_assistant")

# Database / API
MONGO_DB_URI = _env("MONGO_DB_URI")
API_KEY = _env("API_KEY")

# Duration limit
DURATION_LIMIT_MIN = _to_int(_env("DURATION_LIMIT", 999999), 999999)
DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))

# Logger
LOGGER_ID = _parse_logger_id(_env("LOGGER_ID"))
CLONE_LOGGER = LOGGER_ID

# Heroku (optional)
HEROKU_APP_NAME = _env("HEROKU_APP_NAME")
HEROKU_API_KEY = _env("HEROKU_API_KEY")

# Upstream Git (optional)
UPSTREAM_REPO = _env("UPSTREAM_REPO", "https://github.com/netizen-0/DEVAMUSIC")
UPSTREAM_BRANCH = _env("UPSTREAM_BRANCH", "main")
GIT_TOKEN = _env("GIT_TOKEN", None)

# Support links
SUPPORT_CHANNEL = _env("SUPPORT_CHANNEL", "https://t.me/BotzEmpire")
SUPPORT_CHAT = _env("SUPPORT_CHAT", "https://t.me/Yaaro_kimehfill")
CHAT = _env("Shayri", "https://t.me/Matlabi_Duniyah")

# Assistant / Limits
AUTO_LEAVING_ASSISTANT = _to_bool(_env("AUTO_LEAVING_ASSISTANT", False), False)
AUTO_LEAVE_ASSISTANT_TIME = _to_int(_env("ASSISTANT_LEAVE_TIME", "9000"), 9000)

SONG_DOWNLOAD_DURATION = _to_int(_env("SONG_DOWNLOAD_DURATION", "9999999"), 9999999)
SONG_DOWNLOAD_DURATION_LIMIT = _to_int(_env("SONG_DOWNLOAD_DURATION_LIMIT", "9999999"), 9999999)

SERVER_PLAYLIST_LIMIT = _to_int(_env("SERVER_PLAYLIST_LIMIT", "50"), 50)
PLAYLIST_FETCH_LIMIT = _to_int(_env("PLAYLIST_FETCH_LIMIT", "25"), 25)

TG_AUDIO_FILESIZE_LIMIT = _to_int(_env("TG_AUDIO_FILESIZE_LIMIT", "5242880000"), 5242880000)
TG_VIDEO_FILESIZE_LIMIT = _to_int(_env("TG_VIDEO_FILESIZE_LIMIT", "5242880000"), 5242880000)

# Spotify (defaults kept same as your file)
SPOTIFY_CLIENT_ID = _env("SPOTIFY_CLIENT_ID", "1c21247d714244ddbb09925dac565aed")
SPOTIFY_CLIENT_SECRET = _env("SPOTIFY_CLIENT_SECRET", "709e1a2969664491b58200860623ef19")

# Sessions / misc state
STRING1 = _env("STRING_SESSION", "")
STRING2 = _env("STRING_SESSION2", None)

BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

# Images
STREAMI_PICS = [
    "https://i.ibb.co/whgkNq6n/start-img-1.jpg",
    "https://i.ibb.co/q32FdssH/start-img-2.jpg",
]

START_IMG_URL = _env("START_IMG_URL", "https://i.ibb.co/xPjc7tv/help-menu.jpg")
HELP_IMG_URL = _env("HELP_IMG_URL", "https://i.ibb.co/xPjc7tv/help-menu.jpg")
PING_IMG_URL = _env("PING_IMG_URL", "https://i.ibb.co/VWnm6f3f/ping.jpg")

PLAYLIST_IMG_URL = "https://i.ibb.co/gL3ykkyh/play-music.jpg"
STATS_IMG_URL = "https://i.ibb.co/pBqPtFYn/statistics.jpg"
TELEGRAM_AUDIO_URL = "https://i.ibb.co/gL3ykkyh/play-music.jpg"
TELEGRAM_VIDEO_URL = "https://i.ibb.co/gL3ykkyh/play-music.jpg"
STREAM_IMG_URL = "https://i.ibb.co/0VKCS20y/stream.jpg"
SOUNCLOUD_IMG_URL = "https://i.ibb.co/S4sPf3q8/soundcloud.jpg"
YOUTUBE_IMG_URL = "https://i.ibb.co/xShkBVBK/youtube.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://i.ibb.co/XZfMS8Db/spotify.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://i.ibb.co/XZfMS8Db/spotify.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://i.ibb.co/XZfMS8Db/spotify.jpg"

# Validation (same logic, just safe)
if SUPPORT_CHANNEL:
    if not re.match(r"(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://"
        )

if SUPPORT_CHAT:
    if not re.match(r"(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHAT url is wrong. Please ensure that it starts with https://"
        )

# Emoji list
GREET = [
    "💞", "🥂", "🔍", "🧪", "⚡️", "🔥", "🎩", "🌈", "🍷", "🥃", "🥤", "🕊️",
    "🦋", "💌", "🧨"
]
