#Scraper Temel Sınıfı - Tüm site scraperları bu sınıftan türer.

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional
import requests
from bs4 import BeautifulSoup
from ..config import SCRAPE_DAYS


class BaseScraper(ABC):
    """Tüm haber scraper'larının base sınıfı."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8",
        })
        self.cutoff_date = datetime.now() - timedelta(days=SCRAPE_DAYS)

    def get_page(self, url: str, timeout: int = 15) -> Optional[BeautifulSoup]:
        """URL'den sayfa çeker ve BeautifulSoup nesnesi döndürür."""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return BeautifulSoup(response.text, "lxml")
        except Exception as e:
            print(f"[SCRAPER] {url} çekilemedi: {e}")
            return None

    def is_recent(self, tarih: Optional[datetime]) -> bool:
        """Haberin son SCRAPE_DAYS gün içinde olup olmadığını kontrol eder."""
        if tarih is None:
            return True  # Tarih yoksa dahil et
        return tarih >= self.cutoff_date

    @abstractmethod
    def scrape(self) -> list[dict]:
        """
        Haberleri çeker.
        Her haber şu alanları içermeli:
        - baslik: str
        - icerik: str
        - yayin_tarihi: datetime | None
        - kaynak_adi: str
        - kaynak_url: str
        """
        pass
