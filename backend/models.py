from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class HaberCreate(BaseModel):
    """Yeni haber oluşturmak için model."""
    baslik: str
    icerik: str
    haber_turu: str
    konum_metni: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    yayin_tarihi: Optional[datetime] = None
    kaynak_adi: str
    kaynak_url: str
    kaynaklar: List[str] = []  # Aynı haber birden fazla kaynakta ise


class HaberResponse(BaseModel):
    """Frontend'e döndürülecek haber modeli."""
    id: str
    baslik: str
    icerik: str
    haber_turu: str
    konum_metni: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    yayin_tarihi: Optional[str] = None
    kaynak_adi: str
    kaynak_url: str
    kaynaklar: List[str] = []
    ilce: Optional[str] = None


class ScrapeResponse(BaseModel):
    """Scraping sonuç raporu."""
    toplam_cekilen: int
    yeni_kayit: int
    mukerrer: int
    konum_bulunamayan: int
    mesaj: str


class StatsResponse(BaseModel):
    """İstatistik endpoint'i için model."""
    toplam_haber: int
    tur_dagilimi: dict
    ilce_dagilimi: dict
    son_guncelleme: Optional[str] = None
