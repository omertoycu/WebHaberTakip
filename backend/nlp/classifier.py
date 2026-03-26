"""
NLP - Haber Türü Sınıflandırıcı
Anahtar kelime tabanlı, öncelik sıralı sınıflandırma
"""
import re

# Öncelik sırasına göre kategoriler ve anahtar kelimeler
# Her haber yalnızca TEK bir türle etiketlenir (önce eşleşen kazanır)
# ÖNEMLİ: Su Kesintisi, Elektrik Kesintisi'nden ÖNCE kontrol edilmeli
# çünkü "kesinti" kelimesi her ikisinde de geçebilir.
KATEGORI_ANAHTAR_KELIMELER = {
    "Trafik Kazası": [
        r"\btrafik kaza", r"\bzincirleme kaza", r"\barraç devril", r"\btakla at", r"\byayaya çarp", 
        r"\byoldan çık", r"\bşarampole", r"\baraç çarpış", r"\baraç kontrolden çık"
    ],
    "Yangın": [
        r"\byangın", r"\balevler", r"\bitfaiye ekipleri sevk", r"\balevlere teslim", 
        r"\byandı\b", r"\bitfaiye müdahale", r"\bbaca yangın", r"\bçatı yangın", r"\borman yangın"
    ],
    "Elektrik Kesintisi": [
        r"\belektrik kesintisi\b", r"\belektrikler kesil", r"\btrafo patla", r"\benerji verileme",
        r"\belektrik arıza", r"\belektrik verileme", r"\belektriksiz kal",
    ],
    "Hırsızlık": [
        r"\bhırsızlık\b", r"\bsoygun\b", r"\bkapkaç\b", r"\byankesici", r"\bdolandırıcı", r"\bgasp edil",
        r"\bkasadaki\b", r"\bçalın", r"\bçalarak", r"\bvurgun\b", r"\beve gir", r"\bgirerek çal"
    ],
    "Kültürel Etkinlikler": [
        r"\bfestival\b", r"\bkonser\b", r"\bsergi\b", r"\bfuar\b", r"\bsempozyum\b", 
        r"\bkonferans\b", r"\btiyatro oyunu\b", r"\bmüzikal\b", r"\bkültür merkezi", r"\betkinlik düzenle",
        r"\bkursiyer", r"\batölye çalışması", r"\bgösterisi\b", r"\bsergisi\b"
    ]
}

# Embedding tabanlı benzerlik için kategori açıklamaları
KATEGORI_ACIKLAMALARI = {
    "Trafik Kazası": "Trafik kazası, zincirleme kaza, araç devrilmesi, yaralanma, ambulans sevk edildi, otoyol karayolu yol kapandı kaza yaptı tır devrildi",
    "Yangın": "Yangın felaketi, alevler, itfaiye müdahalesi, bina yangını, çatı yangını",
    "Elektrik Kesintisi": "Elektrik kesintisi, trafo patlaması, sedaş, enerji verilememesi",
    "Hırsızlık": "Hırsızlık, soygun, dolandırıcılık, gasp, yankesicilik",
    "Kültürel Etkinlikler": "Kültürel etkinlik, konser, festival, tiyatro, sergi, şenlik",
    "Genel": "Genel yerel haberler, siyaset, belediye kararı, spor kulübü, eğitim okul, temel atma töreni, futbol maçı, asayiş olayları cinayet cinayeti polis operasyonu"
}

# Negatif kelimeler: Eğer bu kelimeler varsa, "Kültürel Etkinlikler" olamaz.
KULTUREL_NEGATIF = [
    r"uyuşturucu", r"polis", r"gözaltı", r"tutuklan", r"cezaevi", r"hapis", r"silah", 
    r"bıçak", r"kaza", r"cinayet", r"ceset", r"operasyon", r"çete", r"kaçakçı", r"yasa dışı", r"şüpheli", r"suç örgütü"
]

# "Trafik Kazası" negatif kontrol: cinayet, kavga gibi durumları kaza sanmasın
TRAFIK_NEGATIF = [
    r"cinayet", r"bıçakla", r"vurdu", r"silahlı", r"kavga", r"tartışma", r"intihar", r"faili meçhul",
    r"tır park", r"otopark", r"park sorunu", r"parkına dönüştü", r"park alanı", r"park edilm"
]

# "Elektrik Kesintisi" negatif kontrol: su ile ilgili kelimeler varsa elektrik kesintisi olmamalı
ELEKTRIK_NEGATIF = [
    r"\bsu kesintisi", r"\bsu kesil", r"\bsular kesil", r"\bsu arıza", 
    r"\bsu şebekesi", r"\bİSU\b", r"\bsu verileme", r"\bsulara ne zaman",
    r"\bsular ne zaman", r"\bsu hattı", r"\bsu boru",
]

def siniflandir(baslik: str, icerik: str, embedding: list = None) -> str:
    """
    Haber başlık ve içeriğini analiz ederek türünü belirler.
    Önce Kural Bazlı (Regex) kontrol yapılır.
    Eğer 'Diğer' çıkarsa ve embedding sağlanmışsa Yapay Zeka (Zero-Shot) ile tahmin edilir.
    """
    arama_metni = baslik.lower()  # Regex sadece BAŞLIKTA arasın (Gürültü önleme)
    negative_metin = (baslik + " " + icerik).lower() # Negatif kontroller için tam metin
    
    # --- 1. KURAL TABANLI SINIFLANDIRMA (Hızlı ve Kesin) ---
    for kategori, pattern_list in KATEGORI_ANAHTAR_KELIMELER.items():
        # Negatif kontroller
        if kategori == "Kültürel Etkinlikler" and any(re.search(p, negative_metin) for p in KULTUREL_NEGATIF):
            continue
        if kategori == "Trafik Kazası" and any(re.search(p, negative_metin) for p in TRAFIK_NEGATIF):
            continue
        if kategori == "Elektrik Kesintisi" and any(re.search(p, negative_metin, re.IGNORECASE) for p in ELEKTRIK_NEGATIF):
            continue
            
        # Pozitif kontrol
        for pattern in pattern_list:
            if re.search(pattern, arama_metni, re.IGNORECASE):
                return kategori

    # --- 2. YAPAY ZEKA DESTEKLİ (EMBEDDING) SINIFLANDIRMA (Fallback) ---
    if embedding is not None and isinstance(embedding, list) and len(embedding) > 0:
        try:
            from .embedding_helper import kosinüs_benzerlik, metni_vektorlesitir
            
            # Kategori vektörlerini önbelleğe al (Lazy initialization)
            # Embedding model yüklemesi ve pre-computation
            if not hasattr(siniflandir, "kategori_vektorleri"):
                print("[AI] Kategori referans vektörleri hesaplanıyor...")
                siniflandir.kategori_vektorleri = {}
                for kat, aciklama in KATEGORI_ACIKLAMALARI.items():
                    # E5 için açıklamaları query gibi mi passage gibi mi gömelim?
                    # Açıklamalar kısa olduğu için query gibi gömülebilir, ama biz passage ile test edin demiştik.
                    # Aslında "passage: " ile simetrik benzerlik iyi sonuç verir.
                    siniflandir.kategori_vektorleri[kat] = metni_vektorlesitir(aciklama)
                print("[AI] Kategori referans vektörleri hazır.")
            
            benzerlikler = {}
            for kat, kat_vec in siniflandir.kategori_vektorleri.items():
                benzerlikler[kat] = kosinüs_benzerlik(embedding, kat_vec)
                
            en_iyi_kat = max(benzerlikler, key=benzerlikler.get)
            en_iyi_skor = benzerlikler[en_iyi_kat]
            
            # E5-large için eşik değer testi (Genellikle 0.75-0.85 arası iyidir)
            # 0.78 ve üzeri genellikle ilgili kategoridedir.
            MIN_BENZERLIK = 0.78
            
            if en_iyi_skor >= MIN_BENZERLIK:
                tahmin = en_iyi_kat
                print(f"[AI] Embedding Benzerliği ile sınıflandırıldı: {tahmin} (Skor: {en_iyi_skor:.2f})")
                
                if tahmin == "Genel":
                    return "Diğer"
                
                # AI tahminini negatif filtrelerle doğrula
                if tahmin == "Kültürel Etkinlikler" and any(re.search(p, arama_metni) for p in KULTUREL_NEGATIF):
                    return "Diğer"
                if tahmin == "Trafik Kazası" and any(re.search(p, arama_metni) for p in TRAFIK_NEGATIF):
                    return "Diğer"
                if tahmin == "Elektrik Kesintisi" and any(re.search(p, arama_metni) for p in ELEKTRIK_NEGATIF):
                    return "Diğer"
                
                return tahmin
            else:
                print(f"[AI] Benzerlik çok düşük: {en_iyi_kat} ({en_iyi_skor:.2f}) < {MIN_BENZERLIK}")
                
        except Exception as e:
            print(f"[HATA] Embedding sınıflandırma çalışmadı: {e}")
            
    return "Diğer"

def tum_anahtar_kelimeler() -> dict:
    """Rapor için tüm anahtar kelime listesini döndürür."""
    return KATEGORI_ANAHTAR_KELIMELER
