from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

# .env Variable
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Connect
uri = "mongodb+srv://" + DB_USER + ":" + DB_PASSWORD + DB_HOST

# Create client
client = MongoClient(uri, server_api=ServerApi("1"))

# Test koneksi ke database
try:
    client.admin.command("ping")
except Exception as kesalahan:
    print(kesalahan)

# Database
def use_db():
    return client["bce-cargo"]