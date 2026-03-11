"""
Bizim Yaka (bizimyaka.com) Scraper
"""
import re
from .base_scraper import BaseScraper
from .cagdaskocaeli import CagdasKocaeliScraper


class BizimYakaScraper(CagdasKocaeliScraper):
    BASE_URL = "https://www.bizimyaka.com"
    KAYNAK_ADI = "Bizim Yaka"

    def scrape(self) -> list[dict]:
        haberler = []
        kategoriler = ["/", "/haberler/", "/son-haberler/", "/yerel/"]
        ziyaret_edilen = set()

        for kategori in kategoriler:
            soup = self.get_page(self.BASE_URL + kategori)
            if not soup:
                continue

            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                if re.search(r'/\d{4,}|/(haber|detay|icerik)/', href) and len(href) > 10:
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
                            if len(haberler) >= 50:
                                break

        print(f"[{self.KAYNAK_ADI}] {len(haberler)} haber çekildi.")
        return haberler
