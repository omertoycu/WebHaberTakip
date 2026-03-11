"""
MongoDB bağlantı katmanı - Motor async driver kullanılıyor.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from .config import MONGODB_URI, DB_NAME

# Uygulama başladığında bağlantı oluşturulur
_client: AsyncIOMotorClient = None


async def get_database():
    """Motor async veritabanı nesnesini döndürür."""
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
        )
    return _client[DB_NAME]


async def init_db():
    """Koleksiyonlara index'leri ekler. Bağlantı hatası sunucuyu durdurmaz."""
    try:
        db = await get_database()
        # Haberler koleksiyonu index'leri
        await db.haberler.create_index("kaynak_url", unique=False)
        await db.haberler.create_index("yayin_tarihi")
        await db.haberler.create_index("haber_turu")
        await db.haberler.create_index("ilce")
        # Geocode önbellek koleksiyonu
        await db.geocode_cache.create_index("adres", unique=True)
        print("[DB] Index'ler oluşturuldu.")
    except Exception as e:
        print(f"[DB] UYARI: Index oluşturulamadı (MongoDB bağlantısı kurulamıyor olabilir): {e}")
        print("[DB] Sunucu çalışmaya devam ediyor. Lütfen MongoDB bağlantısını kontrol edin.")


async def close_db():
    """Uygulama kapanırken bağlantıyı kapat."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
