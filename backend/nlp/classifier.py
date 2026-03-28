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
        r"\byoldan çık", r"\bşarampole", r"\baraç çarpış", r"\baraç kontrolden", r"\bmotosiklet kaza",
        r"\botomobil devril", r"\bkamyon devril", r"\btıra çarp"
    ],
    "Yangın": [
        r"\byangın", r"\balev", r"\bitfaiye\b", r"\balevlere teslim", 
        r"\byandı\b", r"\byanarak", r"\bkül oldu", r"\bdumandan etkilend", r"\bkundakla"
    ],
    "Elektrik Kesintisi": [
        r"\belektrik kesintis", r"\belektrikler kes", r"\btrafo patla", r"\benerji verileme",
        r"\belektrik arıza", r"\belektriksiz kal", r"\bSEDAŞ", r"\bplanlı kesinti"
    ],
    "Hırsızlık": [
        r"\bhırsız", r"\bsoygun", r"\bkapkaç", r"\byankesici", r"\bdolandırıc", r"\bgasp\b",
        r"\bkasadaki\b", r"\bçalın", r"\bçalarak", r"\bçaldı", r"\bvurgun\b", r"\beve girerek", 
        r"\bçalmaya çalış", r"\bsahte dekont", r"\bsoydular"
    ],
    "Kültürel Etkinlikler": [
        r"\bfestival\b", r"\bkonser\b", r"\bsergi\b", r"\bfuar\b", r"\bsempozyum\b", 
        r"\bkonferans\b", r"\btiyatro\b", r"\bmüzikal\b", r"\bkültür merkezi", r"\betkinlik\b",
        r"\bsöyleşi", r"\bimza günü", r"\bgösterime gir", r"\batölye çalış"
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
    r"tır park", r"otopark", r"park sorunu", r"parkına dönüştü", r"park alanı", r"park edilm",
    r"yolda bırakt", r"zam\b", r"yakaland", r"hükümlü", r"aranan", r"dolandırıcı"
]

# "Elektrik Kesintisi" negatif kontrol: su ile ilgili kelimeler varsa elektrik kesintisi olmamalı
ELEKTRIK_NEGATIF = [
    r"\bsu kesintisi", r"\bsu kesil", r"\bsular kesil", r"\bsu arıza", 
    r"\bsu şebekesi", r"\bİSU\b", r"\bsu verileme", r"\bsulara ne zaman",
    r"\bsular ne zaman", r"\bsu hattı", r"\bsu boru",
    r"jeotermal", r"doğalgaz", r"gaz kesintisi", r"isyan"
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
            # 0.81 ve üzeri ilgili kategoriye çok yakındır.
            MIN_BENZERLIK = 0.81
            
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
