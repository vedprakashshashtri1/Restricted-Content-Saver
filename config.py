"""Runtime configuration loaded from environment variables.

Streamlit Community Cloud exposes root-level entries from its Secrets editor as
environment variables. Keep real credentials out of this repository.
"""

from os import getenv


def required(name: str) -> str:
    value = getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


API_ID = int(required("API_ID"))
API_HASH = required("API_HASH")
BOT_TOKEN = required("BOT_TOKEN")
OWNER_ID = [int(user_id) for user_id in required("OWNER_ID").split()]
MONGO_DB = required("MONGO_DB")
LOG_GROUP = int(required("LOG_GROUP"))
CHANNEL_ID = int(required("CHANNEL_ID"))

FREEMIUM_LIMIT = int(getenv("FREEMIUM_LIMIT", "1000"))
PREMIUM_LIMIT = int(getenv("PREMIUM_LIMIT", "500000"))
WEBSITE_URL = getenv("WEBSITE_URL", "gplinks.com")
AD_API = getenv("AD_API", "")
STRING = getenv("STRING", "")
DEFAULT_SESSION = getenv("DEFAULT_SESSION", getenv("DEFAUL_SESSION", ""))
YT_COOKIES = getenv("YT_COOKIES", "")
INSTA_COOKIES = getenv("INSTA_COOKIES", "")
