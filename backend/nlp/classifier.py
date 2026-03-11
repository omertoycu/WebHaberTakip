"""
NLP - Haber Türü Sınıflandırıcı
Anahtar kelime tabanlı, öncelik sıralı sınıflandırma
"""
import re

# Öncelik sırasına göre kategoriler ve anahtar kelimeler
# Her haber yalnızca TEK bir türle etiketlenir (önce eşleşen kazanır)
KATEGORI_ANAHTAR_KELIMELER = {
    "Trafik Kazası": [
        r"\btrafik kaza", r"\bzincirleme kaza", r"\barraç devril", r"\btakla at", r"\byayaya çarp", 
        r"\byoldan çık", r"\bşarampole", r"\baraç çarpış", r"\baraç kontrolden çık"
    ],
    "Yangın": [
        r"\byangın", r"\balev topu", r"\bitfaiye ekipleri sevk", r"\balevlere teslim"
    ],
    "Elektrik Kesintisi": [
        r"\belektrik kesintisi\b", r"\belektrikler kesil", r"\btrafo patla", r"\benerji verileme"
    ],
    "Hırsızlık": [
        r"\bhırsızlık\b", r"\bsoygun\b", r"\bkapkaç\b", r"\byankesici", r"\bdolandırıcı", r"\bgasp edil"
    ],
    "Kültürel Etkinlikler": [
        r"\bfestival\b", r"\bkonser\b", r"\bsergi\b", r"\bfuar\b", r"\bsempozyum\b", 
        r"\bkonferans\b", r"\btiyatro oyunu\b", r"\bmüzikal\b"
    ]
}

# Negatif kelimeler: Eğer bu kelimeler varsa, "Kültürel Etkinlikler" olamaz.
KULTUREL_NEGATIF = [
    r"uyuşturucu", r"polis", r"gözaltı", r"tutuklan", r"cezaevi", r"hapis", r"silah", 
    r"bıçak", r"kaza", r"cinayet", r"ceset", r"operasyon", r"çete", r"kaçakçı", r"yasa dışı", r"şüpheli", r"suç örgütü"
]

def siniflandir(baslik: str, icerik: str) -> str:
    """
    Haber başlık ve içeriğini analiz ederek türünü belirler.
    Öncelik sırası korunur. Kelime kökleri/sınırları regex ile kontrol edilir.
    """
    arama_metni = (baslik + " " + icerik).lower()

    for kategori, pattern_list in KATEGORI_ANAHTAR_KELIMELER.items():
        if kategori == "Kültürel Etkinlikler":
            # Negatif kontrol
            negatif_var = any(re.search(p, arama_metni) for p in KULTUREL_NEGATIF)
            if negatif_var:
                continue

        # Pozitif kontrol
        for pattern in pattern_list:
            if re.search(pattern, arama_metni):
                return kategori

    return "Diğer"

def tum_anahtar_kelimeler() -> dict:
    """Rapor için tüm anahtar kelime listesini döndürür."""
    return KATEGORI_ANAHTAR_KELIMELER
