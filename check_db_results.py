import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.kocaeli_haberler
    
    docs = await db.haberler.find({}).to_list(100)
    for index, doc in enumerate(docs):
        print(f"[{doc.get('haber_turu')}] {doc.get('baslik')}")

if __name__ == "__main__":
    asyncio.run(check_db())
