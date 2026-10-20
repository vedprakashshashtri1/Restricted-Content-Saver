"""Streamlit launcher and health page for the Telegram bot."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import streamlit as st


REQUIRED_SECRETS = (
    "API_ID",
    "API_HASH",
    "BOT_TOKEN",
    "OWNER_ID",
    "MONGO_DB",
    "LOG_GROUP",
    "CHANNEL_ID",
)


def load_streamlit_secrets() -> list[str]:
    """Copy root-level Streamlit secrets into the child process environment."""
    missing: list[str] = []
    for name in REQUIRED_SECRETS:
        value = st.secrets.get(name)
        if value is None or str(value).strip() == "":
            missing.append(name)
        else:
            os.environ[name] = str(value)

    for name in (
        "FREEMIUM_LIMIT",
        "PREMIUM_LIMIT",
        "WEBSITE_URL",
        "AD_API",
        "STRING",
        "DEFAULT_SESSION",
        "YT_COOKIES",
        "INSTA_COOKIES",
    ):
        value = st.secrets.get(name)
        if value is not None:
            os.environ[name] = str(value)
    return missing


@st.cache_resource
def start_bot() -> subprocess.Popen[bytes]:
    """Start one bot worker for this Streamlit server process."""
    return subprocess.Popen(
        [sys.executable, "-m", "devgagan"],
        cwd=Path(__file__).resolve().parent,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )


st.set_page_config(page_title="Restricted Content Saver", page_icon="🤖")
st.title("Restricted Content Saver")
st.caption("Telegram bot launcher and deployment status")

missing = load_streamlit_secrets()
if missing:
    st.error("Missing required Streamlit secrets: " + ", ".join(missing))
    st.info("Add the secrets in your app's Settings → Secrets, then reboot the app.")
    st.stop()

process = start_bot()
return_code = process.poll()

if return_code is None:
    st.success("Bot worker is running.")
    st.metric("Worker PID", process.pid)
else:
    st.error(f"Bot worker stopped with exit code {return_code}.")
    st.info("Check the Streamlit app logs, correct the configuration, and reboot the app.")

st.write(f"Python: `{sys.version.split()[0]}`")
st.warning(
    "Streamlit Community Cloud can sleep inactive apps. If you need a Telegram bot "
    "to run continuously, use an always-on worker host instead."
)
