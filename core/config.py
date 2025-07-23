import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPERADMIN_ID = list(map(int, os.getenv("SUPERADMIN_ID", "").split(",")))