from VIP_INNOCENT.core.bot import INNOCENT
from VIP_INNOCENT.core.dir import dirr
from VIP_INNOCENT.core.git import git
from VIP_INNOCENT.core.userbot import Userbot
from VIP_INNOCENT.misc import dbb, heroku
from pyrogram import Client
from SafoneAPI import SafoneAPI
from .logging import LOGGER

dirr()
git()
dbb()
heroku()

app = INNOCENT()
api = SafoneAPI()
userbot = Userbot()

from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
