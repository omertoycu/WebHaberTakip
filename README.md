# 🗺️ Kocaeli Haber İzleme Sistemi (Web Haber Takip)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)

## 📝 Proje Hakkında
**Kocaeli Haber İzleme Sistemi**, Kocaeli bölgesi ve ilçelerindeki yerel haberleri (özellikle asayiş ve acil durum olaylarını) otomatik olarak tarayan, **Doğal Dil İşleme (NLP)** ve **Makine Öğrenmesi** teknikleriyle analiz eden ve kullanıcılarına interaktif bir harita üzerinden anlık görselleştiren akıllı bir web platformudur.

Kaza, yangın, hırsızlık, elektrik kesintisi gibi önemli haberler yapay zeka tarafından metinden tespit edilir, olay yeri otomatik olarak coğrafi koordinatlara dönüştürülür ve haritada ilgili ikon/renk kodlarıyla işaretlenir.

## 🚀 Özellikler

*   **🕵️ Otomatik Haber Toplama (Web Scraping)**: Düzenli aralıklarla yerel kaynaklardan asenkron çalışan haber botları aracılığıyla veri çekilir *(BeautifulSoup, HTTPX)*.
*   **🧠 Yapay Zeka Destekli Analiz (NLP)**:
    *   **Metin Sınıflandırma**: Haberlerin türü (Trafik Kazası, Yangın, Elektrik Kesintisi, Hırsızlık, Kültürel Etkinlikler vb.) `Sentence-Transformers` ve `Spacy` kullanılarak belirlenir.
    *   **Varlık İsmi Tanıma (NER)**: Haber içeriğindeki lokasyon, ilçe, mahalle, cadde adresleri otomatik olarak çıkarılır.
*   **🌍 Geocoding & Harita Gösterimi**: Tespit edilen lokasyon metinleri, koordinatlara çevrilir *(Geocoding)* ve olaylar **Google Maps API** desteği ile dinamik haritaya aktarılır.
*   **🔍 Gelişmiş Filtreleme Arayüzü**: Tarih, olay türü ve Kocaeli'nin ilçelerine özgü esnek filtreleme/arama deneyimi.
*   **⚡ Modern ve Ölçeklenebilir Mimari**: Asenkron çalışan `FastAPI` ve `MotorM (MongoDB)` altyapısı sayesinde yüksek performans.

## 🛠️ Teknolojiler

### Backend
*   **Dil**: Python 3.x
*   **Framework**: FastAPI, Uvicorn
*   **Veritabanı**: MongoDB (Motor / PyMongo)
*   **NLP & ML Modelleri**: Spacy, Sentence-Transformers, Scikit-Learn
*   **Web Scraping & Ağ İstekleri**: BeautifulSoup4, lxml, Requests, HTTPX, Aiohttp
*   **Veri Doğrulama**: Pydantic

### Frontend
*   **Yapı**: HTML5, Vanilla JavaScript (ES6+), CSS3
*   **Haritalandırma**: Google Maps API
*   **Tasarım Dili**: Inter Font (Google Fonts), özel ve responsive UI

## ⚙️ Kurulum ve Çalıştırma (Lokal Ortam)

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyebilirsiniz.

### 1. Gereksinimler
- Python 3.8 veya daha üstü bir sürüm
- MongoDB (Yerel kurulum veya Atlas Cloud URI)
- Google Maps API Key

### 2. Projeyi Klonlayın ve Bağımlılıkları Kurun
```bash
git clone https://github.com/kullaniciadi/WebHaberTakip.git
cd WebHaberIzleme
```

Sanal bir ortam (virtual environment) oluşturmanız tavsiye edilir:
```bash
python -m venv .venv
# Windows için (CMD/Powershell)
.venv\Scripts\activate
# Linux/Mac için
source .venv/bin/activate
```

Gerekli olan tüm Python paketlerini kurun:
```bash
pip install -r requirements.txt
```

*(Not: `Spacy` Türkçe modeli için kurulum esnasında `python -m spacy download tr_core_news_trf` (veya benzer bir modelin) indirilmesi gerekebilir).*

### 3. Çevresel Değişkenler (.env)
Proje kök dizininde bulunan `.env` dosyasını (eğer yoksa oluşturarak) kendi yapılandırmalarınızla doldurun:

```env
# MongoDB Bağlantısı
MONGO_URI=mongodb://localhost:27017/ 
DB_NAME=kocaeli_haber_db

# (İsteğe bağlı) Google Maps vb. API Key'ler de buralardan yönetilebilir.
MAPS_API_KEY=YOUR_GOOGLE_MAPS_API_KEY
```

### 4. Uygulamayı Başlatın
Tüm ayarlar tamamlandıktan sonra ana giriş noktasından projeyi çalıştırın:
```bash
python run.py
```

Uygulama başarıyla başlatıldığında terminalde şu çıktı belirecektir:
```text
============================================================
  Kocaeli Haber İzleme Sistemi
  Backend API: http://localhost:8000
  Swagger UI:  http://localhost:8000/docs
  Frontend:    http://localhost:8000
============================================================
```
Tarayıcınızdan `http://localhost:8000` adresine giderek uygulamayı kullanmaya başlayabilirsiniz! 🎉

## 📁 Proje Klasör Yapısı

```text
📦WebHaberIzleme
 ┣ 📂backend           # FastAPI sunucusu ve iş mantığı
 ┃ ┣ 📂nlp             # Doğal Dil İşleme (Sınıflandırma, NER) komut dosyaları
 ┃ ┣ 📂scrapers        # Web scraping (haber çekme) botları
 ┃ ┣ 📜main.py         # FastAPI Root uygulaması
 ┃ ┣ 📜models.py       # Pydantic ve Veritabanı modelleri
 ┃ ┣ 📜database.py     # MongoDB bağlantı konfigürasyonu
 ┃ ┣ 📜geocoding.py    # Lokasyon verilerinin (Enlem/Boylam) dönüştürülmesi
 ┃ ┗ 📜pipeline.py     # Tüm sürecin (Scrape -> NLP -> DB) entegre edildiği orkestrasyon dosyası
 ┣ 📂frontend          # Kullanıcı Arayüzü (UI)
 ┃ ┣ 📜index.html      # Ana web sayfası ve yapı
 ┃ ┣ 📜styles.css      # Özelleştirilmiş tasarım kuralları
 ┃ ┗ 📜app.js          # Arayüz dinamiği, filtrelemeler ve Harita işlemleri
 ┣ 📜run.py            # Projeyi başlatan (Uvicorn) yürütücü scipt
 ┣ 📜requirements.txt  # Python paket bağımlılıkları listesi
 ┣ 📜.env              # Gizli / Çevresel değişkenler
 ┗ 📜README.md         # (Bu dosya)
```
