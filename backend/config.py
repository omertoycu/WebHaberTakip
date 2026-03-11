import os
from dotenv import load_dotenv

# .env dosyasını projenin kök dizininden yükle
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "kocaeli_haberler")
GOOGLE_GEOCODING_KEY = os.getenv("GOOGLE_GEOCODING_KEY", "")
GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_KEY", "")

# Scraping ayarları
SCRAPE_DAYS = 3  # Son kaç günün haberleri çekilecek
SIMILARITY_THRESHOLD = 0.90  # %90 benzerlik eşiği

# Kocaeli ilçeleri (geocoding için arama zenginleştirmesi)
KOCAELI_DISTRICTS = [
    "İzmit", "Gebze", "Körfez", "Darıca", "Çayırova", "Dilovası",
    "Gölcük", "Karamürsel", "Kandıra", "Başiskele", "Derince",
    "İzmit Merkez", "Kartepe", "Kocaeli"
]
