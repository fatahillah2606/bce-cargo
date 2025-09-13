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

def get_client():
    """
    Coba connect ke MongoDB Atlas, kalau gagal fallback ke localhost.
    """
    # URI ke Atlas
    atlas_uri = f"mongodb+srv://{DB_USER}:{DB_PASSWORD}{DB_HOST}"
    local_uri = "mongodb://localhost:27017"

    # Coba Atlas dulu
    try:
        client = MongoClient(atlas_uri, server_api=ServerApi("1"))
        client.admin.command("ping")  # test koneksi
        return client
    except Exception as e:
        print(f"Gagal connect Atlas: {e}")
        print("Coba connect ke MongoDB lokal...")
        try:
            client = MongoClient(local_uri)
            client.admin.command("ping")
            return client
        except Exception as e2:
            print(f"Gagal connect ke MongoDB lokal juga: {e2}")
            raise e2

# Client aktif
client = get_client()

# Database
def use_db():
    return client["bce-cargo"]
