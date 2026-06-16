#import libraries
import os
from dotenv import load_dotenv

load_dotenv()

#mbta api
MBTA_API_KEY = os.getenv("MBTA_API_KEY")
MBTA_BASE_URL = "https://api-v3.mbta.com/"
MBTA_ROUTES = ["Red", "Blue", "Orange","Green-B","Green-C","Green-D","Green-E","Blue"]

#database
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "dbname": os.getenv("DB_NAME","postgres"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

#pipeline
FETCH_INTERVAL_MINUTES = int(os.getenv("FETCH_INTERVAL_MINUTES", 2))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "logs/pipeline.log"

def validate():
    missing = [k for k, v in {
        "MBTA_API_KEY": MBTA_API_KEY,
        "DB_PASSWORD": DB_CONFIG["password"],
    }.items() if not v]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")