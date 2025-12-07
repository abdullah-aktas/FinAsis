"""
Documentation Views
Dinamik Markdown Dokümantasyon Görüntüleme
"""
from django.shortcuts import render
from pathlib import Path
from django.conf import settings
import markdown


def render_markdown_doc(request, doc_path):
    """
    Markdown dosyasını HTML'e çevirip render et

    Args:
        doc_path: Döküman yolu (örn: 'kobi/quick-start')
    """
    # Markdown dosya yolunu oluştur
    docs_dir = Path(settings.BASE_DIR) / "docs"

    # Güvenlik: path traversal önleme
    doc_path = doc_path.replace("..", "").strip("/")

    # Dosya yolları dene
    possible_paths = [
        docs_dir / f"{doc_path}.md",
        docs_dir / doc_path / "README.md",
        docs_dir / f"{doc_path.upper()}.md",
    ]

    markdown_file = None
    for path in possible_paths:
        if path.exists() and path.is_file():
            markdown_file = path
            break

    if not markdown_file:
        # Placeholder içerik oluştur
        content_html = generate_placeholder_content(doc_path)
    else:
        # Markdown'ı oku ve HTML'e çevir
        with open(markdown_file, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        # Markdown extensions ile render et
        content_html = markdown.markdown(
            markdown_content,
            extensions=[
                "markdown.extensions.extra",
                "markdown.extensions.codehilite",
                "markdown.extensions.toc",
                "markdown.extensions.tables",
            ],
        )

    # Breadcrumb oluştur
    breadcrumbs = generate_breadcrumbs(doc_path)

    # Title oluştur
    title = format_title(doc_path)

    context = {
        "title": title,
        "content_html": content_html,
        "breadcrumbs": breadcrumbs,
        "doc_path": doc_path,
    }

    return render(request, "common/documentation_page.html", context)


def generate_placeholder_content(doc_path):
    """
    Henüz oluşturulmamış dökümanlar için placeholder HTML
    """
    parts = doc_path.split("/")
    category = parts[0] if len(parts) > 0 else "genel"
    topic = parts[1] if len(parts) > 1 else "konu"

    # Kategori bazlı içerik öneri
    content_suggestions = {
        "kobi": {
            "quick-start": {
                "title": "KOBİ Hızlı Başlangıç Kılavuzu",
                "sections": [
                    "Şirket Oluşturma",
                    "İlk Fatura Girişi",
                    "Dashboard Kullanımı",
                    "Finansal Analiz Başlatma",
                ],
            },
            "financial-analysis": {
                "title": "Finansal Analiz Rehberi",
                "sections": [
                    "Analiz Türleri",
                    "AI Destekli Analiz",
                    "Sağlık Skoru Okuma",
                    "Öneriler ve Aksiyonlar",
                ],
            },
            "budget-planning": {
                "title": "Bütçe Planlama Kılavuzu",
                "sections": [
                    "Bütçe Oluşturma",
                    "Varyans Analizi",
                    "Otomatik Uyarılar",
                    "Bütçe Revizyonu",
                ],
            },
            "cash-flow": {
                "title": "Nakit Akış Yönetimi",
                "sections": [
                    "Nakit Akış Tahmini",
                    "Senaryo Analizi",
                    "Risk Tespiti",
                    "Nakit Sıkışıklığı Önleme",
                ],
            },
        },
        "games": {
            "player-guide": {
                "title": "Oyuncu Rehberi",
                "sections": [
                    "Hesap Oluşturma",
                    "İlk Oyun",
                    "Progression Sistemi",
                    "Liderlik Tablosu",
                ],
            },
            "tradesim": {
                "title": "TradeSim Kullanım Kılavuzu",
                "sections": [
                    "Detaylı bilgi için TRADESIM_KLAVUZU.md dosyasına bakın",
                    "Veya /resources/docs/ sayfasında arama yapın",
                ],
            },
            "finquest": {
                "title": "FinQuest 3D Rehberi",
                "sections": [
                    "Kontroller (WASD)",
                    "Quest Sistemi",
                    "NPC Etkileşimleri",
                    "3D Dünya Keşfi",
                ],
            },
            "esports": {
                "title": "E-Spor Sistemi Rehberi",
                "sections": [
                    "Turnuva Sistemi",
                    "ELO ve Rütbeler",
                    "Sezonlar",
                    "Takım Oluşturma",
                ],
            },
        },
        "ai": {
            "ai-assistant": {
                "title": "AI Asistan Kullanımı",
                "sections": [
                    "Anomali Tespiti",
                    "Risk Analizi",
                    "Akıllı Öneriler",
                    "Otomatik Muhasebe Kaydı",
                ],
            },
            "anomaly-detection": {
                "title": "Anomali Tespiti Rehberi",
                "sections": [
                    "5 Anomali Türü",
                    "Risk Skorlama",
                    "Otomatik Uyarılar",
                    "Aksiyon Önerileri",
                ],
            },
            "recommendations": {
                "title": "AI Öneriler Sistemi",
                "sections": [
                    "Öneri Tipleri",
                    "Güven Skoru",
                    "Öneri Uygulama",
                    "Feedback Sistemi",
                ],
            },
        },
        "blockchain": {
            "audit-trail": {
                "title": "Blockchain Audit Trail",
                "sections": [
                    "SHA-256 Hash",
                    "Proof of Work",
                    "Zincir Doğrulama",
                    "Sertifika İndirme",
                ],
            }
        },
        "accounting": {
            "invoice-management": {
                "title": "Fatura Yönetimi Kılavuzu",
                "sections": [
                    "Fatura Oluşturma",
                    "e-Fatura/e-Arşiv",
                    "Otomatik Fiş",
                    "Fatura Takibi",
                ],
            },
            "chart-of-accounts": {
                "title": "Hesap Planı Rehberi",
                "sections": [
                    "Tek Düzen Hesap Planı",
                    "Hesap Kodları",
                    "Muhasebe Kayıtları",
                    "Örnekler",
                ],
            },
        },
        "finance": {
            "reports": {
                "title": "Finansal Raporlama",
                "sections": [
                    "Bilanço",
                    "Gelir Tablosu",
                    "Nakit Akışı",
                    "Export İşlemleri",
                ],
            },
            "gib-integration": {
                "title": "GİB Entegrasyonu",
                "sections": [
                    "e-Dönüşüm Kurulumu",
                    "Sertifika Tanımlama",
                    "Fatura Gönderimi",
                    "Hata Kodları",
                ],
            },
        },
        "api": {
            "getting-started": {
                "title": "API ile Başlangıç",
                "sections": [
                    "API_DOCUMENTATION.md dosyasına bakın",
                    "Token alma",
                    "İlk istek",
                    "Rate limiting",
                ],
            },
            "webhooks": {
                "title": "Webhook Rehberi",
                "sections": [
                    "Webhook Kurulumu",
                    "Event Türleri",
                    "İmza Doğrulama",
                    "Retry Politikası",
                ],
            },
            "authentication": {
                "title": "API Kimlik Doğrulama",
                "sections": [
                    "Token-based Auth",
                    "API Key Kullanımı",
                    "OAuth2",
                    "Güvenlik İpuçları",
                ],
            },
        },
    }

    # İçerik önerisini al
    suggestion = content_suggestions.get(category, {}).get(
        topic,
        {
            "title": format_title(doc_path),
            "sections": [
                "Bu döküman henüz hazırlanmaktadır",
                "Ana klavuzlara göz atın",
                "Destek ile iletişime geçin",
            ],
        },
    )

    html = f"""
    <div class="alert alert-info" style="border-radius: 16px; border-left: 5px solid #3b82f6;">
        <h4><i class="bi bi-info-circle me-2"></i>Döküman Hazırlanıyor</h4>
        <p>Bu sayfa henüz hazırlanmaktadır. Aşağıdaki konuları içerecektir:</p>
    </div>
    
    <div class="card border-0 shadow-sm" style="border-radius: 20px;">
        <div class="card-body p-4">
            <h3 class="fw-bold mb-4">{suggestion['title']}</h3>
            
            <h5 class="fw-bold mb-3">📋 Kapsanacak Konular:</h5>
            <ul class="list-unstyled">
                {''.join([f'<li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i>{section}</li>' for section in suggestion['sections']])}
            </ul>
            
            <hr class="my-4">
            
            <h6 class="fw-bold mb-3">🔗 Şimdilik Şu Kaynaklara Bakabilirsiniz:</h6>
            <div class="d-flex gap-2 flex-wrap">
                <a href="/docs/KULLANICI_KLAVUZU.md" class="btn btn-outline-primary btn-sm">
                    <i class="bi bi-book me-1"></i>Kullanıcı Klavuzu
                </a>
                <a href="/docs/KOBI_YONETIM_KLAVUZU.md" class="btn btn-outline-success btn-sm">
                    <i class="bi bi-building me-1"></i>KOBİ Rehberi
                </a>
                <a href="/docs/TRADESIM_KLAVUZU.md" class="btn btn-outline-danger btn-sm">
                    <i class="bi bi-controller me-1"></i>TradeSim Rehberi
                </a>
                <a href="/docs/API_DOCUMENTATION.md" class="btn btn-outline-info btn-sm">
                    <i class="bi bi-code-slash me-1"></i>API Docs
                </a>
            </div>
            
            <div class="mt-4 p-3" style="background: rgba(102,126,234,0.05); border-radius: 12px;">
                <strong><i class="bi bi-download me-2"></i>Markdown Dosyalarını İndirin:</strong>
                <p class="mb-0 small text-muted mt-2">
                    Tüm kılavuzlar <code>docs/</code> klasöründe markdown formatında mevcuttur.
                    GitHub'dan görüntüleyebilir veya indirebilirsiniz.
                </p>
            </div>
        </div>
    </div>
    
    <div class="text-center mt-4">
        <a href="/resources/docs/" class="btn btn-primary btn-lg" style="border-radius: 12px;">
            <i class="bi bi-arrow-left me-2"></i>Döküman Ana Sayfasına Dön
        </a>
    </div>
    """

    return html


def generate_breadcrumbs(doc_path):
    """Breadcrumb navigation oluştur"""
    parts = doc_path.split("/")
    breadcrumbs = [{"title": "Dokümantasyon", "url": "/resources/docs/"}]

    cumulative_path = ""
    for i, part in enumerate(parts):
        cumulative_path += part if i == 0 else f"/{part}"
        breadcrumbs.append(
            {
                "title": format_title(part),
                "url": f"/docs/{cumulative_path}",
                "active": i == len(parts) - 1,
            }
        )

    return breadcrumbs


def format_title(text):
    """URL slug'ını başlığa çevir"""
    text = text.replace("-", " ").replace("_", " ")

    # Özel kısaltmalar
    replacements = {
        "kobi": "KOBİ",
        "ai": "AI",
        "api": "API",
        "gib": "GİB",
        "swot": "SWOT",
    }

    words = text.split()
    formatted = []

    for word in words:
        lower_word = word.lower()
        if lower_word in replacements:
            formatted.append(replacements[lower_word])
        else:
            formatted.append(word.capitalize())

    return " ".join(formatted)
