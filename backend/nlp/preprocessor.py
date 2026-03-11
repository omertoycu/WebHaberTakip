"""
NLP - Metin Ön İşleme Modülü
HTML temizleme, boşluk normalizasyonu, özel karakter temizliği
"""
import re
from bs4 import BeautifulSoup


def temizle(metin: str) -> str:
    """Ham haber metnini temizler ve normalize eder."""
    if not metin:
        return ""

    # 1. HTML etiketlerini kaldır
    soup = BeautifulSoup(metin, "lxml")
    metin = soup.get_text(separator=" ")

    # 2. Reklam ve gereksiz kalıpları kaldır (yaygın Türkçe haber sitesi footer'ları)
    reklam_kaliplari = [
        r'Bu haber[^\n]*kaynak[^\n]*\.',
        r'Haber[^\n]*için tıklayın[^\n]*\.',
        r'İlgili Haberler.*',
        r'Yorum Yaz.*',
        r'Yorumlar.*',
        r'Etiketler:.*',
        r'Bu haberi paylaşın.*',
        r'Kaynak:.*$',
        r'Fotoğraf:.*',
        r'AA\s*$', r'DHA\s*$', r'İHA\s*$',
        r'\(BSHA\)',
        r'Haberin\s+devamı\s+için.*',
    ]
    for kalip in reklam_kaliplari:
        metin = re.sub(kalip, '', metin, flags=re.IGNORECASE | re.MULTILINE)

    # 3. URL'leri kaldır
    metin = re.sub(r'https?://\S+', '', metin)

    # 4. E-posta adreslerini kaldır
    metin = re.sub(r'\S+@\S+\.\S+', '', metin)

    # 5. Özel karakterleri temizle (Türkçe harfleri koru)
    metin = re.sub(r'[^\w\s\.,;:!?()\-\'\"ğüşıöçĞÜŞİÖÇ]', ' ', metin)

    # 6. Fazla boşlukları temizle
    metin = re.sub(r'\s+', ' ', metin)

    # 7. Baş ve son boşlukları kaldır
    metin = metin.strip()

    return metin


def baslik_temizle(baslik: str) -> str:
    """Haber başlığını temizler."""
    if not baslik:
        return ""
    # HTML kaldır
    soup = BeautifulSoup(baslik, "lxml")
    baslik = soup.get_text()
    # Fazla boşluk
    baslik = re.sub(r'\s+', ' ', baslik).strip()
    return baslik
