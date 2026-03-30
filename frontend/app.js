/**
 * Kocaeli Haber Haritası - Google Maps + API Integration
 */

// ============================================================
// CONSTANTS & CONFIG
// ============================================================
const KOCAELI_CENTER = { lat: 40.7654, lng: 29.9408 };
const INITIAL_ZOOM = 11;

const KATEGORI_RENK = {
    "Trafik Kazası": "#ef4444",
    "Yangın": "#f97316",
    "Elektrik Kesintisi": "#eab308",
    "Hırsızlık": "#8b5cf6",
    "Kültürel Etkinlikler": "#06b6d4"
};

const KATEGORI_EMOJI = {
    "Trafik Kazası": "🚗",
    "Yangın": "🔥",
    "Elektrik Kesintisi": "⚡",
    "Hırsızlık": "🔒",
    "Kültürel Etkinlikler": "🎵"
};

// ============================================================
// STATE
// ============================================================
let map = null;
let markers = [];
let currentHaberler = [];
let infoWindow = null;
let markersById = {};

// ============================================================
// MAP INITIALIZATION (called by Google Maps callback)
// ============================================================
function initMap() {
    const mapStyles = [
        { elementType: "geometry", stylers: [{ color: "#1a1d27" }] },
        { elementType: "labels.text.stroke", stylers: [{ color: "#1a1d27" }] },
        { elementType: "labels.text.fill", stylers: [{ color: "#8b8fa8" }] },
        { featureType: "road", elementType: "geometry", stylers: [{ color: "#252836" }] },
        { featureType: "road", elementType: "geometry.stroke", stylers: [{ color: "#1e2130" }] },
        { featureType: "road.arterial", elementType: "labels.text.fill", stylers: [{ color: "#5b5f7a" }] },
        { featureType: "road.highway", elementType: "geometry", stylers: [{ color: "#2d3148" }] },
        { featureType: "road.highway", elementType: "labels.text.fill", stylers: [{ color: "#6366f1" }] },
        { featureType: "water", elementType: "geometry", stylers: [{ color: "#0f1117" }] },
        { featureType: "water", elementType: "labels.text.fill", stylers: [{ color: "#5b5f7a" }] },
        { featureType: "poi", elementType: "geometry", stylers: [{ color: "#1e2130" }] },
        { featureType: "poi.park", elementType: "geometry", stylers: [{ color: "#1a2416" }] },
        { featureType: "transit", elementType: "geometry", stylers: [{ color: "#1e2130" }] },
        { featureType: "administrative", elementType: "geometry", stylers: [{ color: "#3d4163" }] },
        { featureType: "administrative.country", elementType: "labels.text.fill", stylers: [{ color: "#8b8fa8" }] },
        { featureType: "administrative.locality", elementType: "labels.text.fill", stylers: [{ color: "#a8abcb" }] },
    ];

    map = new google.maps.Map(document.getElementById("map"), {
        center: KOCAELI_CENTER,
        zoom: INITIAL_ZOOM,
        styles: mapStyles,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: true,
        zoomControlOptions: {
            position: google.maps.ControlPosition.RIGHT_BOTTOM
        },
        fullscreenControlOptions: {
            position: google.maps.ControlPosition.RIGHT_BOTTOM
        }
    });

    infoWindow = new google.maps.InfoWindow({
        maxWidth: 360
    });

    // Info window custom styles injection
    const style = document.createElement('style');
    style.textContent = `
        .iw-container { font-family: 'Inter', sans-serif; color: #f0f2ff; padding: 4px; min-width: 280px; max-width: 340px; }
        .iw-tur-badge { display: inline-flex; align-items: center; gap: 5px; font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; padding: 3px 8px; border-radius: 99px; margin-bottom: 8px; }
        .iw-baslik { font-size: 0.9rem; font-weight: 700; line-height: 1.3; margin-bottom: 8px; color: #f0f2ff; }
        .iw-icerik { font-size: 0.78rem; color: #8b8fa8; line-height: 1.5; margin-bottom: 10px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 8px; }
        .iw-meta { display: flex; flex-direction: column; gap: 3px; margin-bottom: 10px; }
        .iw-meta-item { display: flex; align-items: center; gap: 6px; font-size: 0.72rem; color: #8b8fa8; }
        .iw-meta-item strong { color: #f0f2ff; }
        .iw-kaynaklar { font-size: 0.7rem; color: #6b7280; margin-bottom: 10px; }
        .iw-kaynaklar a { color: #818cf8; text-decoration: none; margin-right: 6px; }
        .iw-footer { display: flex; gap: 8px; }
        .iw-btn-git { flex: 1; background: linear-gradient(135deg, #6366f1, #818cf8); color: white; border: none; border-radius: 7px; padding: 9px 14px; font-size: 0.8rem; font-weight: 600; cursor: pointer; text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 5px; transition: all 0.2s; }
        .iw-btn-git:hover { opacity: 0.9; transform: translateY(-1px); }
        .gm-style-iw { background: #1e2130 !important; padding: 16px !important; border-radius: 12px !important; box-shadow: 0 8px 30px rgba(0,0,0,0.6) !important; }
        .gm-style-iw-d { overflow: hidden !important; }
        .gm-style-iw-tc::after { background: #1e2130 !important; }
        .gm-ui-hover-effect { filter: invert(1) !important; opacity: 0.7 !important; }
        button.gm-ui-hover-effect img { filter: none !important; }
    `;
    document.head.appendChild(style);

    // Harita yüklendi, haberleri çek
    haberleriYukle();
    istatistikleriYukle();
    ilceleriYukle();

    // Tarih alanlarını varsayılan olarak ayarla (son 3 gün)
    const bugun = new Date();
    const ucGunOnce = new Date(bugun);
    ucGunOnce.setDate(ucGunOnce.getDate() - 3);
    document.getElementById('tarih-bitis').value = bugun.toISOString().split('T')[0];
    document.getElementById('tarih-baslangic').value = ucGunOnce.toISOString().split('T')[0];
}

// ============================================================
// DATA FETCHING
// ============================================================
async function haberleriYukle(params = {}) {
    showMapOverlay(true);

    try {
        const queryParams = new URLSearchParams();

        // Tarih
        const baslangic = document.getElementById('tarih-baslangic').value;
        const bitis = document.getElementById('tarih-bitis').value;
        if (baslangic) queryParams.append('tarih_baslangic', baslangic);
        if (bitis) queryParams.append('tarih_bitis', bitis);

        // İlçe
        const ilce = document.getElementById('ilce-select').value;
        if (ilce) queryParams.append('ilce', ilce);

        const url = `${API_BASE}/api/haberler?${queryParams.toString()}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error(`API hatası: ${response.status}`);

        const data = await response.json();
        currentHaberler = data.haberler || [];

        // Seçili kategorileri filtrele
        const secilenTurler = getSecilenTurler();
        const filtreliHaberler = currentHaberler.filter(h => secilenTurler.includes(h.haber_turu));

        markerlariGuncelle(filtreliHaberler);
        haberListesiniGuncelle(filtreliHaberler);

    } catch (error) {
        console.error('Haber yükleme hatası:', error);
        haberListesiniHataGoster(error.message);
    } finally {
        showMapOverlay(false);
    }
}

async function istatistikleriYukle() {
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        if (!response.ok) return;
        const data = await response.json();
        istatistikleriGoster(data);
    } catch (e) {
        console.error('İstatistik hatası:', e);
    }
}

async function ilceleriYukle() {
    try {
        const response = await fetch(`${API_BASE}/api/ilceler`);
        if (!response.ok) return;
        const data = await response.json();
        const select = document.getElementById('ilce-select');
        (data.ilceler || []).forEach(ilce => {
            const option = document.createElement('option');
            option.value = ilce;
            option.textContent = ilce;
            select.appendChild(option);
        });
    } catch (e) {
        console.error('İlçe listesi hatası:', e);
    }
}

// ============================================================
// MARKERS
// ============================================================
function markerlariGuncelle(haberler) {
    // Mevcut markerleri temizle
    markers.forEach(m => m.setMap(null));
    markers = [];
    markersById = {};

    // Jitter (Aynı konumdaki haberleri hafifçe ayırma) işlemi
    const clusteredHaberler = [];
    const konumGruplari = {};
    
    haberler.forEach(h => {
        if (!h.lat || !h.lng) return;
        const key = `${h.lat.toFixed(4)}_${h.lng.toFixed(4)}`;
        if (!konumGruplari[key]) konumGruplari[key] = [];
        konumGruplari[key].push(h);
    });

    Object.values(konumGruplari).forEach(grup => {
        if (grup.length === 1) {
            clusteredHaberler.push({ ...grup[0], orijinal_lat: grup[0].lat, orijinal_lng: grup[0].lng, count: 1 });
        } else {
            grup.forEach((h, i) => {
                const newH = { ...h };
                newH.orijinal_lat = h.lat;
                newH.orijinal_lng = h.lng;

                // Doğal Görünümlü Rastgele Dağılım (Random Scatter)
                const randomRadius = 0.0005 + (Math.random() * 0.0035);
                // Açıyı rastgele belirle (0 - 360 derece arası herhangi bir yön)
                const randomAngle = Math.random() * Math.PI * 2;

                // Koordinatlara rastgele sapmayı ekle
                newH.lat = h.lat + (randomRadius * Math.cos(randomAngle));
                newH.lng = h.lng + (randomRadius * Math.sin(randomAngle));
                newH.count = grup.length;

                clusteredHaberler.push(newH);
            });
        }
    });

    clusteredHaberler.forEach(haber => {
        if (!haber.lat || !haber.lng) return;

        const renk = KATEGORI_RENK[haber.haber_turu] || "#ef4444";
        const emoji = KATEGORI_EMOJI[haber.haber_turu] || "📌";

        // Emoji ve SVG problemini kökten çözen daha şık Canvas ikon oluşturucu
        function createEmojiMarker(color, emojiText) {
            const size = 60;
            const canvas = document.createElement('canvas');
            canvas.width = size;
            canvas.height = size + 10;
            const ctx = canvas.getContext('2d');
            const center = size / 2;

            // Yumuşak Gölge
            ctx.shadowColor = 'rgba(0, 0, 0, 0.4)';
            ctx.shadowBlur = 10;
            ctx.shadowOffsetY = 4;

            // Dış beyaz kalın çerçeve
            ctx.beginPath();
            ctx.arc(center, center, 22, 0, Math.PI * 2);
            ctx.fillStyle = '#ffffff';
            ctx.fill();

            // Gölgeleri kapat (içerik için)
            ctx.shadowColor = 'transparent';

            // İç renkli halka
            ctx.beginPath();
            ctx.arc(center, center, 19, 0, Math.PI * 2);
            ctx.fillStyle = color;
            ctx.fill();

            // Parlama efekti (Glassmorphism dokunuşu)
            const grd = ctx.createLinearGradient(center - 10, center - 15, center + 10, center + 15);
            grd.addColorStop(0, 'rgba(255, 255, 255, 0.4)');
            grd.addColorStop(1, 'rgba(255, 255, 255, 0)');
            
            ctx.beginPath();
            ctx.arc(center, center, 19, 0, Math.PI * 2);
            ctx.fillStyle = grd;
            ctx.fill();

            // Alt yön işaretçisi (Küçük üçgen)
            ctx.beginPath();
            ctx.moveTo(center - 8, center + 18);
            ctx.lineTo(center, center + 28);
            ctx.lineTo(center + 8, center + 18);
            ctx.fillStyle = '#ffffff';
            ctx.fill();
            
            ctx.beginPath();
            ctx.moveTo(center - 6, center + 18);
            ctx.lineTo(center, center + 25);
            ctx.lineTo(center + 6, center + 18);
            ctx.fillStyle = color;
            ctx.fill();

            // Emojiyi tam ortaya çiz
            ctx.font = "20px 'Segoe UI Emoji', Arial";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.shadowColor = 'rgba(0,0,0,0.3)';
            ctx.shadowBlur = 3;
            ctx.shadowOffsetY = 1;
            ctx.fillText(emojiText, center, center + 2);

            return canvas.toDataURL();
        }

        const customIcon = {
            url: createEmojiMarker(renk, emoji),
            scaledSize: new google.maps.Size(48, 56), // Biraz daha büyük ve belirgin
            anchor: new google.maps.Point(24, 52)     // Merkez ve üçgen ucuna odaklı
        };

        const marker = new google.maps.Marker({
            position: { lat: haber.lat, lng: haber.lng },
            map: map,
            icon: customIcon,
            title: haber.baslik,
            animation: google.maps.Animation.DROP,
        });

        marker.addListener("click", () => {
            markeraTikla(marker, haber);
        });

        markers.push(marker);
        markersById[haber.id] = marker;
    });

    // Info barı güncelle
    document.getElementById('marker-count-info').textContent =
        `📍 ${markers.length} haber gösteriliyor`;
}

function markeraTikla(marker, haber) {
    const renk = KATEGORI_RENK[haber.haber_turu] || "#6b7280";
    const emoji = KATEGORI_EMOJI[haber.haber_turu] || "📌";
    const tarih = haber.yayin_tarihi
        ? new Date(haber.yayin_tarihi).toLocaleDateString('tr-TR', { day: '2-digit', month: 'long', year: 'numeric' })
        : '—';

    // Birden fazla kaynak varsa listele
    const kaynakHtml = haber.kaynaklar && haber.kaynaklar.length > 0
        ? `<div class="iw-kaynaklar">
            <strong>📰 Kaynaklar:</strong> 
            ${haber.kaynaklar.slice(0, 3).map((url, i) => `<a href="${url}" target="_blank" rel="noopener">Kaynak ${i + 1}</a>`).join('')}
           </div>`
        : '';

    const content = `
        <div class="iw-container">
            <div class="iw-tur-badge" style="background:${renk}22; color:${renk}; border: 1px solid ${renk}44">
                ${emoji} ${haber.haber_turu}
            </div>
            <div class="iw-baslik">${escapeHtml(haber.baslik)}</div>
            <div class="iw-icerik">${escapeHtml(haber.icerik || '')}</div>
            <div class="iw-meta">
                <div class="iw-meta-item">📅 <span><strong>${tarih}</strong></span></div>
                <div class="iw-meta-item">📍 <span><strong>${escapeHtml(haber.ilce || haber.konum_metni || '—')}</strong></span></div>
                <div class="iw-meta-item">🗞️ <span><strong>${escapeHtml(haber.kaynak_adi || '—')}</strong></span></div>
            </div>
            ${kaynakHtml}
            <div class="iw-footer">
                <a class="iw-btn-git" href="${haber.kaynak_url}" target="_blank" rel="noopener">
                    🔗 Habere Git
                </a>
            </div>
        </div>
    `;

    infoWindow.setContent(content);
    infoWindow.open(map, marker);

    // Haritayı markera yaklaştır
    map.panTo(marker.getPosition());
}

// ============================================================
// RECENT NEWS LIST
// ============================================================
function haberListesiniGuncelle(haberler) {
    const listEl = document.getElementById('haber-listesi');
    const countEl = document.getElementById('haber-count');
    countEl.textContent = haberler.length;

    if (haberler.length === 0) {
        listEl.innerHTML = `
            <div class="loading-placeholder">
                <p style="font-size:1.5rem">🔍</p>
                <p>Filtreye uyan haber bulunamadı.</p>
            </div>`;
        return;
    }

    listEl.innerHTML = haberler.slice(0, 30).map((haber, idx) => {
        const renk = KATEGORI_RENK[haber.haber_turu] || "#6b7280";
        const emoji = KATEGORI_EMOJI[haber.haber_turu] || "📌";
        const tarih = haber.yayin_tarihi
            ? new Date(haber.yayin_tarihi).toLocaleDateString('tr-TR', { day: '2-digit', month: 'short' })
            : '';

        return `
        <div class="haber-card" 
             style="border-left-color: ${renk}" 
             onclick="haberKartaTikla(${idx})"
             id="haber-card-${haber.id}">
            <div class="haber-card-tur" style="color:${renk}">
                ${emoji} ${haber.haber_turu}
            </div>
            <div class="haber-card-baslik">${escapeHtml(haber.baslik)}</div>
            <div class="haber-card-meta">
                <span>📍 ${escapeHtml(haber.ilce || '—')}</span>
                <span>${tarih}</span>
                <span>🗞️ ${escapeHtml(haber.kaynak_adi || '')}</span>
            </div>
        </div>`;
    }).join('');
}

function haberKartaTikla(idx) {
    const secilenTurler = getSecilenTurler();
    const filtreliHaberler = currentHaberler.filter(h => secilenTurler.includes(h.haber_turu));
    const haber = filtreliHaberler[idx];
    if (!haber) return;

    const marker = markersById[haber.id];
    
    if (marker) {
        const position = marker.getPosition();
        map.panTo(position);
        map.setZoom(14);
        markeraTikla(marker, haber);
    } else if (haber.lat && haber.lng) {
        map.panTo({ lat: haber.lat, lng: haber.lng });
        map.setZoom(14);
    }
}

function haberListesiniHataGoster(mesaj) {
    document.getElementById('haber-listesi').innerHTML = `
        <div class="loading-placeholder">
            <p style="font-size:1.5rem">⚠️</p>
            <p style="color:#ef4444">API bağlantı hatası: ${escapeHtml(mesaj)}</p>
            <p style="font-size:0.7rem; color:#5b5f7a">Backend'in çalıştığından emin olun.</p>
        </div>`;
}

// ============================================================
// STATS
// ============================================================
function istatistikleriGoster(data) {
    document.getElementById('stat-toplam').textContent = data.toplam_haber || 0;

    const turStats = document.getElementById('tur-stats');
    const turlar = data.tur_dagilimi || {};
    const max = Math.max(...Object.values(turlar), 1);

    turStats.innerHTML = `<div class="tur-stat-bar">` +
        Object.entries(turlar).map(([tur, sayi]) => {
            const renk = KATEGORI_RENK[tur] || "#6b7280";
            const pct = Math.round((sayi / max) * 100);
            const emoji = KATEGORI_EMOJI[tur] || "📌";
            return `
            <div class="tur-stat-item">
                <span class="tur-stat-label">${emoji} ${tur}</span>
                <div class="tur-bar-track">
                    <div class="tur-bar-fill" style="width:${pct}%; background:${renk}"></div>
                </div>
                <span class="tur-stat-count">${sayi}</span>
            </div>`;
        }).join('') + `</div>`;
}

// ============================================================
// FILTER ACTIONS
// ============================================================
function filtreUygula() {
    haberleriYukle();
}

function filtreleriTemizle() {
    const bugun = new Date();
    const ucGunOnce = new Date(bugun);
    ucGunOnce.setDate(ucGunOnce.getDate() - 3);

    document.getElementById('tarih-baslangic').value = ucGunOnce.toISOString().split('T')[0];
    document.getElementById('tarih-bitis').value = bugun.toISOString().split('T')[0];
    document.getElementById('ilce-select').value = '';

    // Tüm kategorileri seç
    document.querySelectorAll('.cat-check input[type="checkbox"]').forEach(cb => {
        cb.checked = true;
    });

    haberleriYukle();
}

function getSecilenTurler() {
    const checkboxes = document.querySelectorAll('.cat-check input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

// Kategori checkbox değişince anlık filtrele
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.cat-check input[type="checkbox"]').forEach(cb => {
        cb.addEventListener('change', () => {
            const secilenTurler = getSecilenTurler();
            const filtreliHaberler = currentHaberler.filter(h => secilenTurler.includes(h.haber_turu));
            markerlariGuncelle(filtreliHaberler);
            haberListesiniGuncelle(filtreliHaberler);
        });
    });
});

// ============================================================
// SCRAPING
// ============================================================
async function scrapeBaslat() {
    const btn = document.getElementById('scrape-btn');
    const status = document.getElementById('scrape-status');
    const icon = document.getElementById('scrape-icon');

    btn.disabled = true;
    icon.textContent = '⏳';
    status.className = 'scrape-status info';
    status.textContent = '🔄 Haberler çekiliyor... Bu işlem 1-3 dakika sürebilir.';
    status.classList.remove('hidden');

    try {
        // Senkron scrape - sonucu bekle
        const response = await fetch(`${API_BASE}/api/scrape/bekle`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) throw new Error(`Sunucu hatası: ${response.status}`);
        const result = await response.json();

        status.className = 'scrape-status success';
        status.innerHTML = `✅ Tamamlandı!<br>
            📥 Çekilen: <strong>${result.toplam_cekilen}</strong> | 
            ✨ Yeni: <strong>${result.yeni_kayit}</strong><br>
            🔁 Mükerrer: ${result.mukerrer} | ❌ Konum yok: ${result.konum_bulunamayan}`;

        // Haberleri ve istatistikleri yenile
        await haberleriYukle();
        await istatistikleriYukle();

    } catch (error) {
        status.className = 'scrape-status error';
        status.textContent = `❌ Hata: ${error.message}`;
    } finally {
        btn.disabled = false;
        icon.textContent = '🔄';
    }
}

// ============================================================
// UTILITIES
// ============================================================
function showMapOverlay(show) {
    const overlay = document.getElementById('map-overlay');
    if (show) overlay.classList.remove('hidden');
    else overlay.classList.add('hidden');
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#x27;');
}
