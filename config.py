from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
PUBLIC_DOWNLOAD_BASE_URL = os.getenv("PUBLIC_DOWNLOAD_BASE_URL", "").strip()
