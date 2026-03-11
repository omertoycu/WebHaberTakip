"""
Pipeline Orkestrasyonu - Scraping -> NLP -> Geocoding -> MongoDB
"""
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from .database import get_database
from .scrapers import ALL_SCRAPERS
from .nlp.preprocessor import temizle, baslik_temizle
from .nlp.classifier import siniflandir
from .nlp.ner_extractor import konum_cikar
from .nlp.duplicate_detector import metni_vektorlesitir, mukerrer_mu
from .geocoding import koordinat_al


async def pipeline_calistir() -> dict:
    """
    Tam veri hattını çalıştırır:
    1. Tüm sitelerden haber çek
    2. Temizle, sınıflandır, konum çıkar
    3. Mükerrer kontrolü
    4. Geocoding
    5. MongoDB'ye kaydet
    
    Returns: İşlem özeti
    """
    db = await get_database()
    haberler_kol = db.haberler
    cache_kol = db.geocode_cache

    toplam_cekilen = 0
    yeni_kayit = 0
    mukerrer_sayisi = 0
    konum_bulunamayan = 0

    # Scraping (senkron - thread pool'da çalıştır)
    ham_haberler = []
    loop = asyncio.get_event_loop()

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for ScraperClass in ALL_SCRAPERS:
            def run_scraper(cls=ScraperClass):
                try:
                    scraper = cls()
                    return scraper.scrape()
                except Exception as e:
                    print(f"[PIPELINE] {cls.__name__} hata: {e}")
                    return []

            future = loop.run_in_executor(executor, run_scraper)
            futures.append(future)

        results = await asyncio.gather(*futures, return_exceptions=True)
        for result in results:
            if isinstance(result, list):
                ham_haberler.extend(result)
            elif isinstance(result, Exception):
                print(f"[PIPELINE] Scraper exception: {result}")

    toplam_cekilen = len(ham_haberler)
    print(f"[PIPELINE] Toplam {toplam_cekilen} haber çekildi.")

    # Her haberi işle
    for ham in ham_haberler:
        try:
            # 1. Temizle
            baslik = baslik_temizle(ham.get("baslik", ""))
            icerik = temizle(ham.get("icerik", ""))
            kaynak_url = ham.get("kaynak_url", "")
            kaynak_adi = ham.get("kaynak_adi", "")
            yayin_tarihi = ham.get("yayin_tarihi") or datetime.utcnow()

            if not baslik or len(icerik) < 50:
                continue

            # 2. Sınıflandır
            haber_turu = siniflandir(baslik, icerik)

            # Sadece proje kategorilerindeki haberleri işle (Diğer'i atla)
            if haber_turu == "Diğer":
                 continue

            # 3. Konum çıkar
            konum_metni, ilce = konum_cikar(baslik, icerik)

            # Konum bulunamadıysa atla (proje gereksinimi)
            if not konum_metni:
                konum_bulunamayan += 1
                continue

            # 4. Embedding oluştur
            embedding_metin = baslik + " " + icerik[:500]
            embedding = metni_vektorlesitir(embedding_metin)

            # 5. Mükerrer kontrolü
            is_dup, dup_id = await mukerrer_mu(embedding, kaynak_url, haberler_kol)

            if is_dup and dup_id:
                # Sadece kaynak listesini güncelle
                await haberler_kol.update_one(
                    {"_id": __import__("bson").ObjectId(dup_id)},
                    {
                        "$addToSet": {"kaynaklar": kaynak_url},
                        "$set": {"guncelleme_tarihi": datetime.utcnow()}
                    }
                )
                mukerrer_sayisi += 1
                continue

            # 6. Geocoding
            lat, lng = await koordinat_al(konum_metni, cache_kol)

            if lat is None or lng is None:
                konum_bulunamayan += 1
                continue

            # 7. MongoDB'ye kaydet
            belge = {
                "baslik": baslik,
                "icerik": icerik[:2000],  # Fazla yer kaplamaması için kısalt
                "haber_turu": haber_turu,
                "konum_metni": konum_metni,
                "ilce": ilce,
                "lat": lat,
                "lng": lng,
                "yayin_tarihi": yayin_tarihi,
                "kaynak_adi": kaynak_adi,
                "kaynak_url": kaynak_url,
                "kaynaklar": [kaynak_url],
                "embedding": embedding,
                "olusturma_tarihi": datetime.utcnow(),
            }

            await haberler_kol.insert_one(belge)
            yeni_kayit += 1
            print(f"[PIPELINE] ✓ Kaydedildi: {baslik[:60]}...")

        except Exception as e:
            print(f"[PIPELINE] Haber işleme hatası: {e}")
            continue

    sonuc = {
        "toplam_cekilen": toplam_cekilen,
        "yeni_kayit": yeni_kayit,
        "mukerrer": mukerrer_sayisi,
        "konum_bulunamayan": konum_bulunamayan,
        "mesaj": f"{yeni_kayit} yeni haber kaydedildi, {mukerrer_sayisi} mükerrer atlandı."
    }
    print(f"[PIPELINE] Tamamlandı: {sonuc}")
    return sonuc
