"""
NLP - Konum Çıkarım Modülü (NER)
spaCy Türkçe modeli + regex tabanlı Kocaeli ilçe tespiti
"""
import re
from typing import Optional

# spaCy modelini lazy load et (ilk kullanımda yükle)
_nlp = None

# Kocaeli ilçeleri ve mahalleleri - regex için
KOCAELI_ILCELERI = [
    "Başiskele", "Çayırova", "Darıca", "Derince", "Dilovası",
    "Gebze", "Gölcük", "İzmit", "Kandıra", "Karamürsel",
    "Kartepe", "Korfez", "Körfez", "Kocaeli"
]

# İlçe tespiti için regex kalıpları
ILCE_PATTERN = re.compile(
    r'\b(' + '|'.join(KOCAELI_ILCELERI) + r")\b",
    re.IGNORECASE
)

# Mahalle/sokak kalıpları
MAHALLE_PATTERN = re.compile(
    r'([A-ZÇĞİÖŞÜa-zçğışöşü][a-zçğışöşü]+(?:\s[A-ZÇĞİÖŞÜ][a-zçğışöşü]+)*)\s+'
    r'(?:Mahallesi|Mah\.|Mahalle|Sokak|Sok\.|Caddesi|Cad\.|Bulvarı|Blv\.)',
    re.UNICODE
)

# Etkinlik alanları ve önemli lokasyonlar
VENUE_PATTERN = re.compile(
    r'([A-ZÇĞİÖŞÜa-zçğışöşü][a-zçğışöşü]+(?:\s[A-ZÇĞİÖŞÜ][a-zçğışöşü]+)*)\s+'
    r'(?:Kongre Merkezi|Kültür Merkezi|Fuar Alanı|Sanat Galerisi|Spor Salonu|Gösteri Merkezi|Meydanı|Belediyesi|Sekapark|SDKM|Amfitiyatros?u|Stadyumu)',
    re.UNICODE
)


def _get_nlp():
    """spaCy modelini lazy load eder. Birden fazla model dener."""
    global _nlp
    if _nlp is None:
        modeller = ["tr_core_news_trf", "tr_core_news_lg", "tr_core_news_md", "tr_core_news_sm"]
        for model_adi in modeller:
            try:
                import spacy
                _nlp = spacy.load(model_adi)
                print(f"[NER] spaCy modeli yüklendi: {model_adi}")
                return _nlp
            except Exception:
                continue
        print("[NER] Hiçbir Türkçe spaCy modeli bulunamadı. Regex tabanlı NER kullanılacak.")
        _nlp = False  # False = yükleme denendi ama başarısız
    return _nlp


def konum_cikar(baslik: str, icerik: str) -> tuple[Optional[str], Optional[str]]:
    """
    Haber metninden konum bilgisi çıkarır.
    
    Returns:
        (konum_metni, ilce): Konum metni ve tespit edilen ilçe adı
        Konum bulunamazsa (None, None) döner.
    """
    tam_metin = baslik + " " + icerik

    # 1. İlçe tespiti (en spesifik önce)
    ilce_match = ILCE_PATTERN.search(tam_metin)
    ilce = ilce_match.group(1) if ilce_match else None

    # 2. Mahalle/sokak tespiti
    mahalle_match = MAHALLE_PATTERN.search(tam_metin)
    
    # 2.5 Venue (Mekan) tespiti
    venue_match = VENUE_PATTERN.search(tam_metin)
    
    # 3. spaCy NER ile konum varlığı tespiti
    nlp = _get_nlp()
    spacy_konumlar = []
    
    if nlp:
        try:
            # Uzun metinlerde sadece ilk 512 karakter işle (performans)
            doc = nlp(tam_metin[:1000])
            for ent in doc.ents:
                if ent.label_ in ("LOC", "GPE", "FAC"):
                    spacy_konumlar.append(ent.text)
        except Exception as e:
            print(f"[NER] spaCy analiz hatası: {e}")

    # 4. En iyi konum metnini oluştur
    konum_parcalari = []
    
    if venue_match:
        konum_parcalari.append(venue_match.group(0))
        
    if mahalle_match and (not venue_match or mahalle_match.group(0) not in venue_match.group(0)):
        konum_parcalari.append(mahalle_match.group(0))
    
    if ilce and ilce not in konum_parcalari:
        konum_parcalari.append(ilce)
    
    # spaCy bulduğu ama regex'in yakalayamadığı konumları ekle
    for spacy_konum in spacy_konumlar[:2]:  # En fazla 2 spaCy sonucu
        if spacy_konum not in " ".join(konum_parcalari):
            konum_parcalari.append(spacy_konum)

    if not konum_parcalari:
        return None, None

    # Geocoding için "Kocaeli" ekle (doğruluk için)
    konum_metni = ", ".join(konum_parcalari)
    if "Kocaeli" not in konum_metni:
        konum_metni += ", Kocaeli, Türkiye"
    else:
        konum_metni += ", Türkiye"

    return konum_metni, ilce
