import os

from dotenv import load_dotenv


load_dotenv()


ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")


if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
    raise ValueError(
        "Missing ADZUNA_APP_ID or ADZUNA_APP_KEY in .env"
    )