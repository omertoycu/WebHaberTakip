"""
NLP - Mükerrer Haber Tespit Modülü
sentence-transformers + cosine similarity ile %90 eşiği
"""
import numpy as np
from typing import Optional
from sentence_transformers import SentenceTransformer

# Model lazy loading
_model = None

SIMILARITY_THRESHOLD = 0.90


def _get_model():
    """Sentence transformer modelini lazy load eder."""
    global _model
    if _model is None:
        print("[DEDUP] all-MiniLM-L6-v2 modeli yükleniyor...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        print("[DEDUP] Model hazır.")
    return _model


def metni_vektorlesitir(metin: str) -> list:
    """Metni embedding vektörüne çevirir."""
    model = _get_model()
    embedding = model.encode(metin, normalize_embeddings=True)
    return embedding.tolist()


def kosinüs_benzerlik(vec1: list, vec2: list) -> float:
    """İki vektör arasındaki kosinüs benzerliğini hesaplar."""
    a = np.array(vec1)
    b = np.array(vec2)
    # Normalize edilmiş vektörler için dot product = cosine similarity
    return float(np.dot(a, b))


async def mukerrer_mu(
    yeni_embedding: list,
    yeni_kaynak_url: str,
    haberler_koleksiyonu
) -> tuple[bool, Optional[str]]:
    """
    Yeni haberin veritabanındaki haberlerle benzerliğini kontrol eder.
    
    Returns:
        (is_duplicate, existing_doc_id): Mükerrer mi ve varsa mevcut belge ID'si
    """
    # Son 7 gündeki haberleri kontrol et (performans optimizasyonu)
    from datetime import datetime, timedelta
    yedi_gun_once = datetime.utcnow() - timedelta(days=7)
    
    cursor = haberler_koleksiyonu.find(
        {"yayin_tarihi": {"$gte": yedi_gun_once}},
        {"embedding": 1, "kaynak_url": 1, "kaynaklar": 1}
    )
    
    async for doc in cursor:
        if "embedding" not in doc or not doc["embedding"]:
            continue
        
        # Aynı kaynak URL zaten kayıtlıysa kesin mükerrer
        if doc.get("kaynak_url") == yeni_kaynak_url:
            return True, str(doc["_id"])
        
        if yeni_kaynak_url in doc.get("kaynaklar", []):
            return True, str(doc["_id"])
        
        # Benzerlik hesapla
        benzerlik = kosinüs_benzerlik(yeni_embedding, doc["embedding"])
        
        if benzerlik >= SIMILARITY_THRESHOLD:
            return True, str(doc["_id"])
    
    return False, None
