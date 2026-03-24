import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Backend importları için kök dizini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import MONGODB_URI, DB_NAME

async def drop_database():
    print(f"[DROP] {MONGODB_URI} üzerinden {DB_NAME} veritabanına bağlanılıyor...")
    client = AsyncIOMotorClient(MONGODB_URI)
    
    await client.drop_database(DB_NAME)
    print(f"[DROP] BAZA SIFIRLANDI: '{DB_NAME}' veritabanı ve içindeki tüm haberler başarıyla silindi!")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(drop_database())
