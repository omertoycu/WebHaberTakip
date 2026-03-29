"""
Özgür Kocaeli (ozgurkocaeli.com.tr) Scraper
"""
import re
from datetime import datetime
from .base_scraper import BaseScraper
from .cagdaskocaeli import CagdasKocaeliScraper  # Tarih parse için


class OzgurKocaeliScraper(CagdasKocaeliScraper):
    BASE_URL = "https://www.ozgurkocaeli.com.tr"
    KAYNAK_ADI = "Özgür Kocaeli"

    def scrape(self) -> list[dict]:
        haberler = []
        kategoriler = ["/", "/kocaeli-haberleri", "/kocaeli-asayis-haberleri"]
        ziyaret_edilen = set()

        for kategori in kategoriler:
            soup = self.get_page(self.BASE_URL + kategori)
            if not soup:
                continue

            kategori_count = 0
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                
                # Geçersiz URL kalıplarını atla
                if "#" in href or "facebook.com/sharer" in href or "twitter.com/intent" in href:
                    continue
                    
                if re.search(r'/\d{4,}[-/]|/(haber|detay|guncel)/', href):
                    if href.startswith("http"):
                        tam_url = href
                    elif href.startswith("/"):
                        tam_url = self.BASE_URL + href
                    else:
                        continue
                    
                    if self.BASE_URL in tam_url and tam_url not in ziyaret_edilen:
                        ziyaret_edilen.add(tam_url)
                        haber = self._haber_cek(tam_url)
                        if haber:
                            haberler.append(haber)
                            kategori_count += 1
                            if kategori_count >= 50:
                                break

        print(f"[{self.KAYNAK_ADI}] {len(haberler)} haber çekildi.")
        return haberler
