"""
Çağdaş Kocaeli (cagdaskocaeli.com.tr) Scraper
"""
from datetime import datetime
from .base_scraper import BaseScraper
import re


class CagdasKocaeliScraper(BaseScraper):
    BASE_URL = "https://www.cagdaskocaeli.com.tr"
    KAYNAK_ADI = "Çağdaş Kocaeli"

    def scrape(self) -> list[dict]:
        haberler = []
        kategoriler = ["/", "/asayis", "/kocaeli-gundem-haberleri"]
        
        ziyaret_edilen = set()
        
        for kategori in kategoriler:
            soup = self.get_page(self.BASE_URL + kategori)
            if not soup:
                continue
            
            # Haber linklerini bul
            linkler = soup.find_all("a", href=True)
            haber_linkleri = []
            
            for link in linkler:
                href = link.get("href", "")
                
                # Geçersiz URL kalıplarını atla
                if "#" in href or "facebook.com/sharer" in href or "twitter.com/intent" in href:
                    continue
                
                # Haber sayfası pattern'i - çoğu haber sitesi /haber/ veya sayısal ID içerir
                if re.search(r'/(haber|detay|news)/|/\d{4}/\d{2}/', href):
                    if href.startswith("http"):
                        tam_url = href
                    else:
                        tam_url = self.BASE_URL + href
                    if tam_url not in ziyaret_edilen:
                        haber_linkleri.append(tam_url)
                        ziyaret_edilen.add(tam_url)

            for url in haber_linkleri[:50]:  # Her kategoriden max 50 haber
                haber = self._haber_cek(url)
                if haber:
                    haberler.append(haber)

        print(f"[{self.KAYNAK_ADI}] {len(haberler)} haber çekildi.")
        return haberler

    def _haber_cek(self, url: str) -> dict | None:
        soup = self.get_page(url)
        if not soup:
            return None

        try:
            # Başlık
            baslik_el = (
                soup.find("h1") or
                soup.find("h2", class_=re.compile(r"title|baslik|heading", re.I))
            )
            baslik = baslik_el.get_text(strip=True) if baslik_el else ""
            if not baslik:
                return None

            # İçerik
            icerik_el = (
                soup.find("div", class_=re.compile(r"content|icerik|haber-detay|article-body", re.I)) or
                soup.find("article") or
                soup.find("div", class_=re.compile(r"detail|detay", re.I))
            )
            icerik = icerik_el.get_text(separator=" ", strip=True) if icerik_el else ""

            # Tarih
            tarih = self._tarih_bul(soup)
            if tarih and not self.is_recent(tarih):
                return None

            return {
                "baslik": baslik,
                "icerik": icerik,
                "yayin_tarihi": tarih,
                "kaynak_adi": self.KAYNAK_ADI,
                "kaynak_url": url,
            }
        except Exception as e:
            print(f"[{self.KAYNAK_ADI}] Haber parse hatası ({url}): {e}")
            return None

    def _tarih_bul(self, soup) -> datetime | None:
        """Sayfadan yayın tarihini çıkarır."""
        # time etiketi
        time_el = soup.find("time")
        if time_el:
            datetime_attr = time_el.get("datetime", "")
            if datetime_attr:
                try:
                    return datetime.fromisoformat(datetime_attr.replace("Z", "+00:00"))
                except:
                    pass
            metin = time_el.get_text(strip=True)
            return self._parse_turkce_tarih(metin)
        
        # meta etiketi
        meta = soup.find("meta", {"property": "article:published_time"})
        if meta and meta.get("content"):
            try:
                return datetime.fromisoformat(meta["content"].replace("Z", "+00:00"))
            except:
                pass
        
        # Text içinde tarih arama
        metin = soup.get_text()
        return self._parse_turkce_tarih(metin)

    def _parse_turkce_tarih(self, metin: str) -> datetime | None:
        """Türkçe tarih formatlarını parse eder."""
        ay_map = {
            "ocak": 1, "şubat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "haziran": 6,
            "temmuz": 7, "ağustos": 8, "eylül": 9, "ekim": 10, "kasım": 11, "aralık": 12,
            "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
            "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
        }
        
        # DD Ay YYYY formatı
        match = re.search(r'(\d{1,2})\s+([a-zA-ZİıŞşğüöç]+)\s+(\d{4})', metin, re.IGNORECASE)
        if match:
            gun, ay_str, yil = match.groups()
            ay = ay_map.get(ay_str.lower())
            if ay:
                try:
                    return datetime(int(yil), ay, int(gun))
                except:
                    pass
        
        # DD.MM.YYYY formatı
        match = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', metin)
        if match:
            gun, ay, yil = match.groups()
            try:
                return datetime(int(yil), int(ay), int(gun))
            except:
                pass
        
        # YYYY-MM-DD formatı
        match = re.search(r'(\d{4})-(\d{2})-(\d{2})', metin)
        if match:
            yil, ay, gun = match.groups()
            try:
                return datetime(int(yil), int(ay), int(gun))
            except:
                pass
        
        return None
