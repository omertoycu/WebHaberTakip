"""
Yeni Kocaeli (yenikocaeli.com) Scraper
NOT: Bu site sürekli connection timeout verdiği için devre dışı bırakıldı.
"""
from .cagdaskocaeli import CagdasKocaeliScraper


class YeniKocaeliScraper(CagdasKocaeliScraper):
    BASE_URL = "https://www.yenikocaeli.com"
    KAYNAK_ADI = "Yeni Kocaeli"

    def scrape(self) -> list[dict]:
        print(f"[{self.KAYNAK_ADI}] Atlandı (sunucu timeout - devre dışı).")
        return []
