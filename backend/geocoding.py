"""
Geocoding Modülü - Google Geocoding API + MongoDB önbellek
Aynı adres için tekrar API çağrısı yapmayı önler.
"""
import httpx
from typing import Optional
from .config import GOOGLE_GEOCODING_KEY


async def koordinat_al(
    adres: str,
    geocode_cache_koleksiyonu
) -> tuple[Optional[float], Optional[float]]:
    """
    Adres metnini enlem/boylama çevirir.
    Önce MongoDB önbelleğine bakar, bulamazsa Google API'ye sorar.
    
    Returns:
        (lat, lng) veya konum bulunamazsa (None, None)
    """
    if not adres or not adres.strip():
        return None, None

    adres_normalized = adres.strip().lower()

    # 1. Önbellekte var mı kontrol et
    onbellek = await geocode_cache_koleksiyonu.find_one({"adres": adres_normalized})
    if onbellek:
        return onbellek.get("lat"), onbellek.get("lng")

    # 2. Google Geocoding API çağrısı
    if not GOOGLE_GEOCODING_KEY:
        print("[GEOCODING] API anahtarı eksik!")
        return None, None

    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": adres,
            "key": GOOGLE_GEOCODING_KEY,
            "language": "tr",
            "region": "tr"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            data = response.json()

        if data.get("status") == "OK" and data.get("results"):
            sonuc = data["results"][0]
            lat = sonuc["geometry"]["location"]["lat"]
            lng = sonuc["geometry"]["location"]["lng"]

            # Kocaeli sınırları içinde mi kontrol et (yaklaşık bbox)
            # Kocaeli: 40.4 - 41.0 N, 29.6 - 30.8 E
            if not (40.3 <= lat <= 41.2 and 29.4 <= lng <= 31.0):
                print(f"[GEOCODING] Kocaeli dışı koordinat: {adres} -> {lat},{lng}")
                # Yine de kaydet ama None döndür
                await geocode_cache_koleksiyonu.update_one(
                    {"adres": adres_normalized},
                    {"$set": {"adres": adres_normalized, "lat": None, "lng": None, "kocaeli_disi": True}},
                    upsert=True
                )
                return None, None

            # Başarılı sonucu önbelleğe kaydet
            await geocode_cache_koleksiyonu.update_one(
                {"adres": adres_normalized},
                {"$set": {"adres": adres_normalized, "lat": lat, "lng": lng}},
                upsert=True
            )
            return lat, lng

        else:
            # Başarısız - boş da olsa önbelleğe yaz (tekrar deneme önleme)
            print(f"[GEOCODING] Sonuç bulunamadı: {adres} -> {data.get('status')}")
            await geocode_cache_koleksiyonu.update_one(
                {"adres": adres_normalized},
                {"$set": {"adres": adres_normalized, "lat": None, "lng": None}},
                upsert=True
            )
            return None, None

    except Exception as e:
        print(f"[GEOCODING] Hata: {adres} -> {e}")
        return None, None
