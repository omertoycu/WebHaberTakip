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
        # --- Multimedya bildirim kalıpları ---
        r'[Hh]aber albümü için resme tıklayın',
        r'[Ff]oto(?:ğraf)?\s+(?:albümü|galerisi)\s+için\s+(?:resme\s+)?tıklayın',
        r'[Vv]ideo için play.{0,5}[ea] tıklayın',
        r'[Vv]ideo için tıklayın',
        r'[Rr]esmi? büyütmek için tıklayın',
        r'Büyütmek için resm[ei] tıklayın',
        r'\d+\s+[Hh]aber albümü için resme tıklayın',

        # --- Döviz Kuru / Finans Ticker Şeritleri ---
        # "Thursday, 26 March 2026 Dolar 44,3595 0,06 Euro 51.." gibi
        r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s*,?\s*\d{1,2}\s+\w+\s+\d{4}\s+Dolar[\s\S]{0,300}',
        r'(?:Pazartesi|Salı|Çarşamba|Perşembe|Cuma|Cumartesi|Pazar)\s*,?\s*\d{1,2}\s+\w+\s+\d{4}\s+Dolar[\s\S]{0,300}',
        r'Dolar\s+\d[\d.,]+\s+[\d.,-]+\s+Euro\s+\d[\d.,]+[\s\S]{0,250}',
        r'Dolar\s+\d[\d.,]+\s+[\d.,-]+\s+(?:Euro|Sterlin|Altın|Gümüş)[\s\S]{0,300}',
        # Bağımsız finans satırları
        r'(?:Euro|Sterlin|Altın|Gümüş|Brent Petrol)\s+\d[\d.,]+\s+[\d.,-]+',

        # --- Haber yönlendirme kalıpları ---
        r'Bu haber\b.{0,60}kaynak.{0,30}\.',
        r'Haber\b.{0,30}için tıklayın.{0,10}\.',
        r'İlgili Haberler\b',
        r'\bYorum Yaz\b',
        r'\bYorumlar\b',
        r'Etiketler\s*:',
        r'Bu haberi paylaşın',
        r'Kaynak\s*:',
        r'Fotoğraf\s*:',
        r'\bAA\s*$', r'\bDHA\s*$', r'\bİHA\s*$',
        r'\(BSHA\)',
        r'Haberin\s+devamı\s+için',
        r'Taraf sayısının fazlalığı nedeniyle',

        # --- Sosyal medya paylaşım butonları ---
        r'(?:(?:WhatsApp|Twitle|Twitter|Facebook|Instagram|Telegram|LinkedIn|Pinterest)\s*)+(?:ile\s+)?(?:Paylaş|paylaş|PAYLAŞ)',
        r'\bPaylaş\s*[-–]\s*',
        r'\bPAYLAŞ\b',
        r'\bpaylaş\b(?:\s+[-–]\s*)?',
        r'\b(?:WhatsApp|Twitle|Twitter)\b(?=\s+(?:WhatsApp|Twitle|Twitter|Facebook|Instagram|Telegram|Paylaş|paylaş|PAYLAŞ))',
        r'\bTwitle\b',

        # --- Abone olma çağrıları ---
        r'\bABONE\s+OL\b',
        r'\bAbone\s+Ol\b',
        r'\bAbone\s+olun\b',
        r'Bülten(?:e|imize)\s+(?:abone|kayıt)\s+ol(?:un|mak)',
        r'Kanalımıza\s+abone\s+olun',
        r'(?:Google|YouTube)\s+[Hh]aberler(?:e|de)\s+(?:abone|takip)\s+(?:ol(?:un)?|edin)',
        r'Haberleri takip edin',

        # --- Reklam kalıpları ---
        r'(?:Google|Adsense)\s+(?:reklam|ilan)(?:lar)?(?:ı)?',
        r'\bReklam\b',
        r'Sponsorlu\s+(?:içerik|haber)',
        r'reklam\s+alanı',

        # --- Okumaya devam / Sıradaki haber ---
        r'(?:Okumaya|Habere)\s+devam(?:\s+(?:et|edin))?',
        r'Bir sonraki haber(?:e geç)?',
        r'Sıradaki haber',
        r'Devamını oku(?:yun)?',

        # --- Yerel Spam Reklamlar ve Seri İlanlar ---
        r'ÇATI USTASI[\s\S]*',
        r'HURDA GAZETE[\s\S]*',
        r'İlanlarınız hem gazete[\s\S]*',
        r'Gün sayısı arttıkça[\s\S]*',
        # Telefon numaralı ilan kalıpları (05xx xxx xx xx)
        r'(?:Tel|Telefon|Gsm|İletişim)\s*(?::|;)?\s*0?\d{3}\s*\d{3}\s*\d{2}\s*\d{2}',
        r'\b0\d{3}\s+\d{3}\s+\d{2}\s+\d{2}\b',
        # Fiyat içeren seri ilan satırları
        r'Kilo\s+ile\s+[\s\S]{0,100}satılır',
        r'\b\d+\s*TL\b\s*(?:Tel|Telefon)',

        # --- Telif / Kaynak / Copyright ---
        r'Tüm hakları saklıdır\.?',
        r'©\s*\d{4}',
        r'Bu habere ilk yorumu siz yapın',
        r'Habere yorum yapın',
        r'Son güncelleme\s*:\s*\d{1,2}[./]\d{1,2}[./]\d{2,4}',
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
