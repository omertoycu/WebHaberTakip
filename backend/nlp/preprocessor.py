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
        # --- Mevcut kalıplar (düzeltilmiş - greedy .* kaldırıldı) ---
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

        # --- Sosyal medya paylaşım butonları ---
        # Sıralı platform adları + Paylaş (WhatsApp Twitle Paylaş gibi)
        r'(?:(?:WhatsApp|Twitle|Twitter|Facebook|Instagram|Telegram|LinkedIn|Pinterest)\s*)+(?:ile\s+)?(?:Paylaş|paylaş|PAYLAŞ)',
        # Büyütme linki
        r'Büyütmek için resm[ei] tıklayın',
        # Tek başına paylaş ifadeleri
        r'\bPaylaş\s*[-–]\s*',
        r'\bPAYLAŞ\b',
        r'\bpaylaş\b(?:\s+[-–]\s*)?',
        # Tek başına platform adları (haber içeriğinde bağımsız çıkan)
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
        
        # --- Yerel Spam Reklamlar ---
        r'ÇATI USTASI[\s\S]*',
        r'HURDA GAZETE[\s\S]*',
        r'İlanlarınız hem gazete[\s\S]*',
        r'Gün sayısı arttıkça[\s\S]*',

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
