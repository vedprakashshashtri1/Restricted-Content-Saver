import asyncio
import logging
import time
import aiohttp
from pyrogram import Client
from pyrogram.enums import ParseMode 
from config import API_ID, API_HASH, BOT_TOKEN, STRING, MONGO_DB, DEFAULT_SESSION, OWNER_ID
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
    {"command": "start", "description": "Check I'm Alive ⚡️"},
    {"command": "batch", "description": "Extract in bulk 🔥"},
    {"command": "settings", "description": "Configure Your Settings ⚙️"},
    {"command": "cancel", "description": "Cancel Ongoing Batch Process 🛑"},
    {"command": "login", "description": "Login To Your Account 🔑"},
    {"command": "logout", "description": "Logout Your Account 🔓"},
    {"command": "adl", "description": "Download audio from 30+ sites 📩"},
    {"command": "dl", "description": "Download videos from 30+ sites 🎊"},
    {"command": "transfer", "description": "Gift premium to others 🎁"},
    {"command": "plan", "description": "Check our premium plans 🗓️"},
    {"command": "speedtest", "description": "Check The Server Speed 🏎️"},
    {"command": "stats", "description": "Get Statistics Of The Bot 📊"},
    {"command": "lock", "description": "Protect Your Channel From Extraction (Owner Only) 🔒"},
    {"command": "add", "description": "Add User To Premium (Owner Only) ➕"},
    {"command": "rem", "description": "Remove User From Premium (Owner Only) ‼️"},
    {"command": "freez", "description": "Remove All Expired User (Owner Only) 🧊"},
    {"command": "gcast", "description": "Send Message To All Users (Owner Only) 🌐"},
    {"command": "acast", "description": "Send Message To All Users With Tag (Owner Only) 🌐"},
    {"command": "restart", "description": "Restart The Bot (Owner Only) 👼"},
]


async def register_bot_commands():
    """Replace legacy command menus for the default, private and owner scopes."""
    targets = [
        ({"type": "default"}, None),
        ({"type": "all_private_chats"}, None),
    ]
    for language_code in ("en", "hi", "ru"):
        targets.append(({"type": "all_private_chats"}, language_code))
    for owner_id in OWNER_ID:
        targets.append(({"type": "chat", "chat_id": owner_id}, None))
        for language_code in ("en", "hi", "ru"):
            targets.append(({"type": "chat", "chat_id": owner_id}, language_code))

    endpoint = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands"
    updated = 0
    async with aiohttp.ClientSession() as session:
        for scope, language_code in targets:
            payload = {"commands": BOT_COMMANDS, "scope": scope}
            if language_code:
                payload["language_code"] = language_code
            async with session.post(endpoint, json=payload) as response:
                result = await response.json(content_type=None)
                if response.status != 200 or not result.get("ok"):
                    raise RuntimeError(
                        f"Telegram rejected bot commands for {scope}/{language_code}: "
                        f"{result.get('description', response.status)}"
                    )
                updated += 1
    LOGGER.info("Registered %s commands across %s Telegram menu scopes.", len(BOT_COMMANDS), updated)

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
        await register_bot_commands()
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

