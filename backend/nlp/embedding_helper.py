"""
NLP - Merkezi Embedding ve Vektörleştirme Modülü
`intfloat/multilingual-e5-large` modeli kullanılarak Türkçe ve Çok Dilli gömme (embedding) üretilir.
"""
import numpy as np
from sentence_transformers import SentenceTransformer

_model = None
MODEL_NAME = 'intfloat/multilingual-e5-large'

def _get_model():
    """Sentence transformer modelini lazy load eder."""
    global _model
    if _model is None:
        print(f"[EMBEDDING] {MODEL_NAME} modeli yükleniyor...")
        _model = SentenceTransformer(MODEL_NAME)
        print("[EMBEDDING] Model hazır.")
    return _model

def metni_vektorlesitir(metin: str, is_query: bool = False) -> list:
    """
    Metni embedding vektörüne çevirir.
    E5 modelleri için:
    - Soru/Kısa Arama (Query) için: prefix "query: "
    - Doküman/Uzun Metin (Passage) için: prefix "passage: "
    Sınıflandırma ve Mükerrer Tespiti gibi simetrik görevlerde,
    iki tarafa da "passage: " eklenmesi önerilir.
    """
    model = _get_model()
    # Simetrik benzerlik için "passage: " kullanıyoruz.
    prefix = "query: " if is_query else "passage: "
    processed_metin = f"{prefix}{metin}"
    
    embedding = model.encode(processed_metin, normalize_embeddings=True)
    return embedding.tolist()

def kosinüs_benzerlik(vec1: list, vec2: list) -> float:
    """İki vektör arasındaki kosinüs benzerliğini hesaplar."""
    a = np.array(vec1)
    b = np.array(vec2)
    # Normalize edilmiş vektörler için dot product = cosine similarity
    return float(np.dot(a, b))
