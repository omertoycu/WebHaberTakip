# backend/scrapers/__init__.py
from .cagdaskocaeli import CagdasKocaeliScraper
from .ozgurkocaeli import OzgurKocaeliScraper
from .seskocaeli import SesKocaeliScraper
from .yenikocaeli import YeniKocaeliScraper
from .bizimyaka import BizimYakaScraper

ALL_SCRAPERS = [
    CagdasKocaeliScraper,
    OzgurKocaeliScraper,
    SesKocaeliScraper,
    YeniKocaeliScraper,
    BizimYakaScraper,
]
