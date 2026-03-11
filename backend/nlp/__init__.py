# backend/nlp/__init__.py
from .preprocessor import temizle, baslik_temizle
from .classifier import siniflandir
from .ner_extractor import konum_cikar
from .duplicate_detector import metni_vektorlesitir, mukerrer_mu
