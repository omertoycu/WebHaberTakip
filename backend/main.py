"""
FastAPI Ana Uygulama
Kocaeli Haber İzleme Sistemi - Backend API
"""
from fastapi import FastAPI, Query, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional
from datetime import datetime, timedelta
import os

from .database import get_database, init_db, close_db
from .pipeline import pipeline_calistir
from .models import ScrapeResponse, StatsResponse


app = FastAPI(
    title="Kocaeli Haber İzleme Sistemi",
    description="Web scraping tabanlı kentsel haber izleme ve harita görselleştirme API'si",
    version="1.0.0"
)

# CORS - Frontend için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Frontend static files
frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.on_event("startup")
async def startup():
    await init_db()
    print("[APP] Uygulama başlatıldı.")


@app.on_event("shutdown")
async def shutdown():
    await close_db()


@app.get("/")
async def root():
    """Frontend index.html'i serve et."""
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"mesaj": "Kocaeli Haber İzleme Sistemi API'sine hoş geldiniz!"}


@app.get("/api/haberler")
async def haberler_listesi(
    tur: Optional[str] = Query(None, description="Haber türü filtresi"),
    ilce: Optional[str] = Query(None, description="İlçe filtresi"),
    tarih_baslangic: Optional[str] = Query(None, description="Başlangıç tarihi (YYYY-MM-DD)"),
    tarih_bitis: Optional[str] = Query(None, description="Bitiş tarihi (YYYY-MM-DD)"),
    limit: int = Query(200, le=500, description="Maksimum haber sayısı"),
):
    """
    Filtrelenmiş haber listesini JSON olarak döndürür.
    Harita üzerinde göstermek için konum bilgisi (lat/lng) içerir.
    """
    db = await get_database()
    filtre = {}

    if tur:
        filtre["haber_turu"] = tur

    if ilce:
        filtre["ilce"] = {"$regex": ilce, "$options": "i"}

    tarih_filtresi = {}
    if tarih_baslangic:
        try:
            tarih_filtresi["$gte"] = datetime.strptime(tarih_baslangic, "%Y-%m-%d")
        except ValueError:
            pass

    if tarih_bitis:
        try:
            bitis = datetime.strptime(tarih_bitis, "%Y-%m-%d")
            bitis = bitis.replace(hour=23, minute=59, second=59)
            tarih_filtresi["$lte"] = bitis
        except ValueError:
            pass

    if tarih_filtresi:
        filtre["yayin_tarihi"] = tarih_filtresi

    # Varsayılan: son 3 gün
    if not tarih_filtresi and not tur and not ilce:
        uc_gun_once = datetime.utcnow() - timedelta(days=3)
        filtre["yayin_tarihi"] = {"$gte": uc_gun_once}

    cursor = db.haberler.find(
        filtre,
        {"embedding": 0}  # embedding'i döndürme (büyük alan)
    ).sort("yayin_tarihi", -1).limit(limit)

    haberler = []
    async for doc in cursor:
        yer = doc.get("ilce", "")
        if yer:
            yer += ", Kocaeli"
            
        haberler.append({
            "id": str(doc["_id"]),
            "baslik": doc.get("baslik", ""),
            "icerik": str(doc.get("icerik", ""))[:300] + "...",
            "haber_turu": doc.get("haber_turu", "Diğer"),
            "konum_metni": doc.get("konum_metni", ""),
            "ilce": yer,
            "yayin_tarihi": doc.get("yayin_tarihi").isoformat() if isinstance(doc.get("yayin_tarihi"), datetime) else doc.get("yayin_tarihi", datetime.utcnow().isoformat()),
            "kaynak_adi": doc.get("kaynak_adi", ""),
            "kaynak_url": doc.get("kaynak_url", ""),
            "lat": doc.get("lat"),
            "lng": doc.get("lng"),
        })

    return {"haberler": haberler, "toplam": len(haberler)}


@app.post("/api/scrape")
async def scrape_baslat(background_tasks: BackgroundTasks):
    """
    Scraping işlemini arka planda başlatır.
    Tüm haber sitelerinden veri çekip işler.
    """
    background_tasks.add_task(pipeline_calistir)
    return {
        "mesaj": "Scraping işlemi arka planda başlatıldı. /api/stats endpoint'i ile ilerlemeyi takip edebilirsiniz.",
        "durum": "baslatildi"
    }


@app.post("/api/scrape/bekle")
async def scrape_bekle():
    """
    Scraping işlemini senkron çalıştırır ve sonucu bekler.
    Test ve Swagger UI için kullanışlı.
    """
    sonuc = await pipeline_calistir()
    return sonuc


@app.get("/api/stats")
async def istatistikler():
    """Veritabanındaki haberlerin istatistiklerini döndürür."""
    db = await get_database()

    toplam = await db.haberler.count_documents({})

    # Tür dağılımı
    tur_pipeline = [
        {"$group": {"_id": "$haber_turu", "sayi": {"$sum": 1}}},
        {"$sort": {"sayi": -1}}
    ]
    tur_sonuc = await db.haberler.aggregate(tur_pipeline).to_list(20)
    tur_dagilimi = {item["_id"]: item["sayi"] for item in tur_sonuc}

    # İlçe dağılımı
    ilce_pipeline = [
        {"$match": {"ilce": {"$ne": None, "$exists": True}}},
        {"$group": {"_id": "$ilce", "sayi": {"$sum": 1}}},
        {"$sort": {"sayi": -1}},
        {"$limit": 10}
    ]
    ilce_sonuc = await db.haberler.aggregate(ilce_pipeline).to_list(10)
    ilce_dagilimi = {item["_id"]: item["sayi"] for item in ilce_sonuc}

    # Son güncelleme
    son_haber = await db.haberler.find_one({}, sort=[("olusturma_tarihi", -1)])
    son_guncelleme = son_haber.get("olusturma_tarihi").isoformat() if son_haber else None

    return {
        "toplam_haber": toplam,
        "tur_dagilimi": tur_dagilimi,
        "ilce_dagilimi": ilce_dagilimi,
        "son_guncelleme": son_guncelleme
    }


@app.get("/api/ilceler")
async def ilce_listesi():
    """Veritabanındaki benzersiz ilçe listesini döndürür."""
    db = await get_database()
    ilceler = await db.haberler.distinct("ilce")
    return {"ilceler": sorted([i for i in ilceler if i])}
