import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def drop_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.kocaeli_haberler
    await db.haberler.drop()
    print("kocaeli_haberler veritabanındaki 'haberler' koleksiyonu başarıyla silindi.")

if __name__ == "__main__":
    asyncio.run(drop_db())
