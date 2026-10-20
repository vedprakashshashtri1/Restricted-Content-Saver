import asyncio
import logging
import time
from pyrogram import Client
from pyrogram.enums import ParseMode 
from pyrogram.types import BotCommand
from config import API_ID, API_HASH, BOT_TOKEN, STRING, MONGO_DB, DEFAULT_SESSION
from telethon.sync import TelegramClient
from motor.motor_asyncio import AsyncIOMotorClient

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)

LOGGER = logging.getLogger(__name__)

BOT_COMMANDS = [
    BotCommand("start", "Check I'm Alive ⚡️"),
    BotCommand("batch", "Extract in bulk 🔥"),
    BotCommand("settings", "Configure Your Settings ⚙️"),
    BotCommand("cancel", "Cancel Ongoing Batch Process 🛑"),
    BotCommand("login", "Login To Your Account 🔑"),
    BotCommand("logout", "Logout Your Account 🔓"),
    BotCommand("adl", "Download audio from 30+ sites 📩"),
    BotCommand("dl", "Download videos from 30+ sites 🎊"),
    BotCommand("transfer", "Gift premium to others 🎁"),
    BotCommand("plan", "Check our premium plans 🗓️"),
    BotCommand("speedtest", "Check The Server Speed 🏎️"),
    BotCommand("stats", "Get Statistics Of The Bot 📊"),
    BotCommand("lock", "Protect Your Channel From Extraction (Owner Only) 🔒"),
    BotCommand("add", "Add User To Premium (Owner Only) ➕"),
    BotCommand("rem", "Remove User From Premium (Owner Only) ‼️"),
    BotCommand("freez", "Remove All Expired User (Owner Only) 🧊"),
    BotCommand("gcast", "Send Message To All Users (Owner Only) 🌐"),
    BotCommand("acast", "Send Message To All Users With Tag (Owner Only) 🌐"),
    BotCommand("restart", "Restart The Bot (Owner Only) 👼"),
]

botStartTime = time.time()

app = Client(
    "pyrobot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=50,
    parse_mode=ParseMode.MARKDOWN
)

sex = TelegramClient('sexrepo', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

if STRING:
    pro = Client("ggbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING)
else:
    pro = None


if DEFAULT_SESSION:
    userrbot = Client("userrbot", api_id=API_ID, api_hash=API_HASH, session_string=DEFAULT_SESSION)
else:
    userrbot = None

telethon_client = TelegramClient('telethon_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# MongoDB setup
tclient = AsyncIOMotorClient(MONGO_DB)
tdb = tclient["telegram_bot"]  # Your database
token = tdb["tokens"]  # Your tokens collection

async def create_ttl_index():
    """Ensure the TTL index exists for the `tokens` collection."""
    await token.create_index("expires_at", expireAfterSeconds=0)

# Run the TTL index creation when the bot starts
async def setup_database():
    await create_ttl_index()
    print("MongoDB TTL index created.")

async def restrict_bot():
    global BOT_ID, BOT_NAME, BOT_USERNAME
    await setup_database()
    await app.start()
    try:
        await app.set_bot_commands(BOT_COMMANDS)
        LOGGER.info("Registered %s Telegram bot commands.", len(BOT_COMMANDS))
    except Exception:
        LOGGER.exception("Could not register Telegram bot commands.")
    getme = await app.get_me()
    BOT_ID = getme.id
    BOT_USERNAME = getme.username
    BOT_NAME = f"{getme.first_name} {getme.last_name}" if getme.last_name else getme.first_name
    
    if pro:
        await pro.start()
    if userrbot:
        await userrbot.start()

loop.run_until_complete(restrict_bot())

