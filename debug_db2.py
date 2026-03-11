import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os
import re

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from nlp.classifier import KATEGORI_ANAHTAR_KELIMELER

async def debug_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.kocaeli_haberler
    
    t_events = await db.haberler.find({"haber_turu": "Trafik Kazası"}).to_list(100)
    for e in t_events:
        arama_metni = (e.get('baslik', '') + " " + e.get('icerik', '')).lower()
        matched_words = []
        for pattern in KATEGORI_ANAHTAR_KELIMELER["Trafik Kazası"]:
            if re.search(pattern, arama_metni):
                matched_words.append(pattern)
        
        # Sadece bizim aradığımız "Bakan Göktaş" veya "Alaaddin Sarı" gibi olanları veya hepsinin eşleşmesini yazdır
        print(f"[{e.get('kaynak_adi')}] TITLE: {e.get('baslik')}")
        print(f"MATCHED: {matched_words}")

if __name__ == "__main__":
    asyncio.run(debug_db())
