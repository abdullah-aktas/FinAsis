# -*- coding: utf-8 -*-
"""
FinAsis Help Content System
Kullanıcılar için yardım içerikleri ve hızlı ipuçları
"""

# ============================================================================
# MODÜL BAZINDA YARDIM İÇERİKLERİ
# ============================================================================

HELP_CONTENT = {
    # MUHASEBE (ACCOUNTING)
    'accounting': {
        'title': 'Muhasebe Yardımı',
        'icon': 'bi-calculator',
        'sections': [
            {
                'title': 'Fatura Oluşturma',
                'content': '''
                    <h5>Yeni Fatura Nasıl Oluşturulur?</h5>
                    <ol>
                        <li>Muhasebe menüsünden "Faturalar" sayfasına gidin</li>
                        <li>"Yeni Fatura" butonuna tıklayın</li>
                        <li>Müşteri bilgilerini seçin veya yeni müşteri ekleyin</li>
                        <li>Ürün/hizmet satırlarını ekleyin</li>
                        <li>KDV oranını belirleyin (varsayılan %20)</li>
                        <li>"Kaydet ve Onayla" butonuna tıklayın</li>
                    </ol>
                    <div class="alert alert-info">
                        <strong>💡 İpucu:</strong> AI Asistan'ı kullanarak sesli komutla fatura oluşturabilirsiniz!
                    </div>
                ''',
                'video_url': '/help/videos/fatura-olusturma.mp4',
                'related_topics': ['kdv_hesaplama', 'e_fatura', 'odeme_takibi']
            },
            {
                'title': 'Otomatik Fiş Kesme',
                'content': '''
                    <h5>Otomatik Muhasebe Fişi Nasıl Çalışır?</h5>
                    <p>FinAsis, fatura oluşturduğunuzda otomatik olarak muhasebe fişini keser.</p>
                    <ul>
                        <li><strong>Satış Faturası:</strong> Alacak hesabı ve gelir hesabı otomatik işlenir</li>
                        <li><strong>Alış Faturası:</strong> Borç hesabı ve gider hesabı otomatik işlenir</li>
                        <li><strong>KDV:</strong> KDV hesapları otomatik hesaplanır</li>
                    </ul>
                    <div class="alert alert-warning">
                        <strong>⚠️ Dikkat:</strong> Fiş onaylandıktan sonra değiştirilemez. Düzeltme fişi kesilmelidir.
                    </div>
                ''',
                'video_url': None,
                'related_topics': ['fis_onaylama', 'hesap_plani', 'yevmiye_defteri']
            },
            {
                'title': 'Mizan Raporu',
                'content': '''
                    <h5>Mizan Raporu Nasıl Görüntülenir?</h5>
                    <ol>
                        <li>Muhasebe → Defterler → Mizan</li>
                        <li>Dönem seçin (yıl ve ay)</li>
                        <li>"Raporu Göster" butonuna tıklayın</li>
                        <li>Excel veya PDF olarak indirebilirsiniz</li>
                    </ol>
                    <p><strong>Mizan nedir?</strong> Tüm hesapların borç ve alacak toplamlarını gösteren rapordur.</p>
                ''',
                'video_url': '/help/videos/mizan-raporu.mp4',
                'related_topics': ['yevmiye_defteri', 'bilanco', 'gelir_tablosu']
            },
            {
                'title': 'e-Fatura ve e-Arşiv',
                'content': '''
                    <h5>e-Fatura Nasıl Gönderilir?</h5>
                    <ol>
                        <li>Fatura oluşturduktan sonra "e-Fatura Gönder" butonuna tıklayın</li>
                        <li>GİB entegrasyonu otomatik çalışır</li>
                        <li>Gönderim durumunu takip edin</li>
                        <li>e-Arşiv fatura için "e-Arşiv Oluştur" seçeneğini kullanın</li>
                    </ol>
                    <div class="alert alert-warning">
                        <strong>⚠️ Gereksinimler:</strong> e-Fatura göndermek için GİB portalında kayıt ve yetkilendirme gerekir.
                    </div>
                ''',
                'related_topics': ['e-fatura', 'gib', 'e-arsiv']
            },
            {
                'title': 'Gider ve Harcama Yönetimi',
                'content': '''
                    <h5>Giderler Nasıl Kaydedilir?</h5>
                    <ol>
                        <li>Muhasebe → Giderler sayfasına gidin</li>
                        <li>"Yeni Gider" butonuna tıklayın</li>
                        <li>Gider bilgilerini girin (tarih, tutar, açıklama, kategori)</li>
                        <li>Fatura/makbuz ekleyin (opsiyonel)</li>
                        <li>Hesap planından gider hesabını seçin</li>
                        <li>KDV bilgilerini girin</li>
                        <li>Kaydedin</li>
                    </ol>
                ''',
                'related_topics': ['gider', 'harcama', 'makbuz']
            },
            {
                'title': 'Hesap Planı Yönetimi',
                'content': '''
                    <h5>Hesap Planını Nasıl Özelleştirirsiniz?</h5>
                    <ol>
                        <li>Muhasebe → Ayarlar → Hesap Planı sayfasına gidin</li>
                        <li>Mevcut hesapları görüntüleyin</li>
                        <li>Yeni hesap eklemek için "Hesap Ekle" tıklayın</li>
                        <li>Hesap bilgilerini girin (kod, ad, tip, dönem bakiyesi)</li>
                        <li>Üst hesap ilişkisini belirleyin</li>
                        <li>Kaydedin</li>
                    </ol>
                    <div class="alert alert-info">
                        <strong>💡 Varsayılan Plan:</strong> FinAsis TMS/TFRS uyumlu varsayılan hesap planı ile gelir.
                    </div>
                ''',
                'related_topics': ['hesap_plani', 'muhasebe', 'hesap']
            }
        ],
        'quick_tips': [
            'AI Asistan ile sesli komut vererek fatura oluşturabilirsiniz',
            'Toplu fatura yüklemek için Excel import özelliğini kullanın',
            'Fiş onaylamadan önce mutlaka kontrol edin',
            'KDV beyannamesi otomatik oluşturulur',
        ],
        'shortcuts': [
            {'key': 'Alt+F', 'description': 'Yeni Fatura'},
            {'key': 'Alt+M', 'description': 'Mizan Raporu'},
            {'key': 'Alt+Y', 'description': 'Yevmiye Defteri'},
        ]
    },
    
    # FİNANS
    'finance': {
        'title': 'Finans Yardımı',
        'icon': 'bi-cash-stack',
        'sections': [
            {
                'title': 'Nakit Akışı Takibi',
                'content': '''
                    <h5>Nakit Akışınızı Nasıl İzlersiniz?</h5>
                    <ol>
                        <li>Finans → Dashboard sayfasına gidin</li>
                        <li>Nakit Akışı widget'ını görüntüleyin</li>
                        <li>Filtreler ile dönem seçin</li>
                        <li>Grafikten detaylı analiz yapın</li>
                    </ol>
                    <div class="alert alert-success">
                        <strong>✓ Otomatik:</strong> Tüm fatura ve ödemeler otomatik nakit akışına yansır
                    </div>
                ''',
                'related_topics': ['banka_hesaplari', 'odeme_planlama', 'tahsilat']
            },
            {
                'title': 'Banka Entegrasyonu',
                'content': '''
                    <h5>Banka Hesaplarınızı Bağlayın</h5>
                    <p>FinAsis, banka hareketlerinizi otomatik çekebilir.</p>
                    <ol>
                        <li>Finans → Bankalar → Banka Ekle</li>
                        <li>Banka bilgilerini girin</li>
                        <li>API credentials ekleyin</li>
                        <li>"Bağlantıyı Test Et" tıklayın</li>
                    </ol>
                ''',
                'related_topics': ['pos_entegrasyonu', 'virman', 'banka_mutabakati']
            },
            {
                'title': 'KPI Takibi',
                'content': '''
                    <h5>Finansal KPI'ları Nasıl Takip Edersiniz?</h5>
                    <p>FinAsis, temel finansal KPI'ları otomatik hesaplar ve görselleştirir:</p>
                    <ul>
                        <li><strong>Ciro:</strong> Toplam gelir</li>
                        <li><strong>Kar Marjı:</strong> Kar/ciro oranı</li>
                        <li><strong>ROI:</strong> Yatırım getirisi</li>
                        <li><strong>Nakit Akışı:</strong> Giriş ve çıkışlar</li>
                        <li><strong>Borç/Alacak:</strong> Ödeme ve tahsilat durumu</li>
                    </ul>
                    <ol>
                        <li>Finans → Dashboard sayfasına gidin</li>
                        <li>KPI kartlarını görüntüleyin</li>
                        <li>Kartlara tıklayarak detaylı rapor alın</li>
                        <li>Dönem bazlı karşılaştırma yapın</li>
                    </ol>
                ''',
                'related_topics': ['kpi', 'analiz', 'performans']
            },
            {
                'title': 'Bütçe Planlama',
                'content': '''
                    <h5>Bütçe Nasıl Oluşturulur?</h5>
                    <ol>
                        <li>Finans → Bütçe → Yeni Bütçe</li>
                        <li>Bütçe adını ve dönemini belirleyin</li>
                        <li>Gelir ve gider kalemlerini ekleyin</li>
                        <li>Tutar ve kategorileri belirleyin</li>
                        <li>Bütçeyi onaylayın</li>
                        <li>Gerçekleşmeleri takip edin</li>
                    </ol>
                    <div class="alert alert-success">
                        <strong>✓ Otomatik Karşılaştırma:</strong> Bütçe ile gerçekleşmeler otomatik karşılaştırılır.
                    </div>
                ''',
                'related_topics': ['butce', 'planlama', 'takip']
            },
            {
                'title': 'Ödeme ve Tahsilat Takibi',
                'content': '''
                    <h5>Ödemeleri Nasıl Takip Edersiniz?</h5>
                    <ol>
                        <li>Finans → Ödemeler sayfasına gidin</li>
                        <li>Ödeme durumlarını görüntüleyin (Beklemede, Ödendi, Gecikmiş)</li>
                        <li>Ödeme yapmak için ödemeye tıklayın</li>
                        <li>Ödeme yöntemini seçin (Banka, Nakit, Çek, Senet)</li>
                        <li>İşlemi tamamlayın</li>
                    </ol>
                    <p><strong>Tahsilat:</strong> Alacaklarınızı takip edin ve hatırlatıcılar gönderin.</p>
                ''',
                'related_topics': ['odeme', 'tahsilat', 'takip']
            }
        ],
        'quick_tips': [
            'Banka ekstrelerini OCR ile otomatik okutabilirsiniz',
            'Çek/senet takibi için hatırlatıcılar kurulabilir',
            'Nakit akışı tahmini için AI kullanın',
        ]
    },
    
    # AI ASİSTAN
    'ai_assistant': {
        'title': 'AI Asistan Yardımı',
        'icon': 'bi-robot',
        'sections': [
            {
                'title': 'Sesli Komutlar',
                'content': '''
                    <h5>AI Asistan'a Sesli Komut Nasıl Verilir?</h5>
                    <ol>
                        <li>Sağ alttaki mikrofon ikonuna tıklayın</li>
                        <li>"Dinliyor..." yazısını bekleyin</li>
                        <li>Komutunuzu söyleyin (Örn: "Yeni fatura oluştur")</li>
                        <li>AI Asistan işlemi gerçekleştirir</li>
                    </ol>
                    <div class="alert alert-info">
                        <strong>Örnek Komutlar:</strong>
                        <ul>
                            <li>"Bu ay kaç fatura kestim?"</li>
                            <li>"Nakit durumum nedir?"</li>
                            <li>"ABC firmasına fatura kes"</li>
                            <li>"Son ödeme tarihi yaklaşanları göster"</li>
                        </ul>
                    </div>
                ''',
                'related_topics': ['fatura_olusturma', 'finansal_analiz', 'raporlama']
            },
            {
                'title': 'Finansal Analiz',
                'content': '''
                    <h5>AI ile Finansal Analiz</h5>
                    <p>AI Asistan finansal durumunuzu analiz eder ve öneriler sunar.</p>
                    <ul>
                        <li><strong>Risk Analizi:</strong> Finansal risklerinizi değerlendirir</li>
                        <li><strong>Tahminleme:</strong> Gelecek nakit akışını tahmin eder</li>
                        <li><strong>Öneriler:</strong> Maliyet tasarrufu önerileri sunar</li>
                        <li><strong>Benchmark:</strong> Sektör ortalaması ile karşılaştırır</li>
                    </ul>
                ''',
                'related_topics': ['risk_yonetimi', 'butce_planlama', 'tahminleme']
            },
            {
                'title': 'OCR ile Belge Okuma',
                'content': '''
                    <h5>Belgeleri Otomatik Nasıl Okutursunuz?</h5>
                    <ol>
                        <li>AI Asistan → OCR → Belge Yükle</li>
                        <li>Fatura, makbuz veya diğer belge fotoğrafını yükleyin</li>
                        <li>AI otomatik olarak belgeyi okur</li>
                        <li>Çıkarılan verileri kontrol edin</li>
                        <li>Onaylayın ve sisteme kaydedin</li>
                    </ol>
                    <div class="alert alert-success">
                        <strong>✓ Desteklenen Belgeler:</strong> Fatura, makbuz, banka ekstresi, sözleşme, kimlik belgeleri
                    </div>
                ''',
                'related_topics': ['ocr', 'belge', 'otomatik']
            },
            {
                'title': 'Doğal Dil Raporlama',
                'content': '''
                    <h5>Türkçe Raporlama Nasıl Yapılır?</h5>
                    <p>AI Asistan, finansal verilerinizi doğal dilde raporlar:</p>
                    <ol>
                        <li>AI Asistan'a sorun: "Bu ayki finansal durumumu özetle"</li>
                        <li>AI verileri analiz eder ve Türkçe rapor oluşturur</li>
                        <li>Raporu görüntüleyin, düzenleyin veya paylaşın</li>
                        <li>PDF veya Word olarak indirebilirsiniz</li>
                    </ol>
                    <p><strong>Örnek Komutlar:</strong></p>
                    <ul>
                        <li>"Bu ayki ciro ne kadar?"</li>
                        <li>"En çok satan ürünler hangileri?"</li>
                        <li>"Nakit akışı raporu hazırla"</li>
                        <li>"Bütçe sapmalarını göster"</li>
                    </ul>
                ''',
                'related_topics': ['raporlama', 'dogal_dil', 'turkce']
            }
        ],
        'quick_tips': [
            'AI Asistan gizliliğinizi korur - veriler dışarı çıkmaz',
            'Türkçe, İngilizce ve Arapça sesli komut desteklenir',
            'OCR ile belgeleri otomatik okutabilirsiniz',
        ]
    },
    
    # EĞİTİM
    'education': {
        'title': 'Eğitim Yardımı',
        'icon': 'bi-mortarboard',
        'sections': [
            {
                'title': 'Ders Takibi',
                'content': '''
                    <h5>Eğitim Nasıl Alınır?</h5>
                    <ol>
                        <li>Eğitim → Dersler sayfasına gidin</li>
                        <li>İlginizi çeken kursu seçin</li>
                        <li>"Kursa Kayıt Ol" tıklayın</li>
                        <li>Video ve materyalleri takip edin</li>
                        <li>Quiz'leri çözün</li>
                        <li>Sertifikanızı alın (NFT blockchain'de)</li>
                    </ol>
                ''',
                'related_topics': ['sertifika', 'quiz', 'nft_rozet']
            },
            {
                'title': 'FinQuest Görev Sistemi',
                'content': '''
                    <h5>FinQuest Nedir?</h5>
                    <p>FinQuest, finansal okuryazarlığı artırmak için görev bazlı öğrenme sistemidir.</p>
                    <ol>
                        <li>Eğitim → FinQuest sayfasına gidin</li>
                        <li>Mevcut görevleri görüntüleyin</li>
                        <li>Görevleri tamamlayın (örnek: "İlk faturanızı oluşturun")</li>
                        <li>Puan ve rozetler kazanın</li>
                        <li>Liderlik tablosunda yer alın</li>
                    </ol>
                    <div class="alert alert-success">
                        <strong>🎮 Eğlenceli Öğrenme:</strong> Görevleri tamamlayarak oyun gibi öğrenin!
                    </div>
                ''',
                'related_topics': ['finquest', 'gorev', 'oyun']
            },
            {
                'title': 'Öğretmen Paneli',
                'content': '''
                    <h5>Ders Nasıl Oluşturulur? (Öğretmenler İçin)</h5>
                    <ol>
                        <li>Eğitim → Öğretmen Paneli → Derslerim</li>
                        <li>"Yeni Ders Oluştur" tıklayın</li>
                        <li>Ders bilgilerini girin (başlık, açıklama, kategori)</li>
                        <li>Video ve materyalleri ekleyin</li>
                        <li>Quiz soruları oluşturun</li>
                        <li>Dersi yayınlayın</li>
                    </ol>
                    <p><strong>Öğrenci Takibi:</strong> Öğrenci ilerlemelerini ve başarılarını takip edin.</p>
                ''',
                'related_topics': ['ogretmen', 'ders', 'olusturma']
            }
        ],
        'quick_tips': [
            'Başarı rozetleri blockchain\'de saklanır',
            'Öğretmenlerle canlı toplantı yapabilirsiniz',
            'Tüm sertifikalar NFT olarak verilir',
        ]
    },
    
    # OYUNLAR
    'games': {
        'title': 'Oyun Yardımı',
        'icon': 'bi-joystick',
        'sections': [
            {
                'title': 'TradeSim 3D',
                'content': '''
                    <h5>TradeSim Oyunu Nasıl Oynanır?</h5>
                    <p>TradeSim, sanal şirket yönetme simülasyonudur. 3D ortamda işletme yönetimi öğrenirsiniz.</p>
                    <ol>
                        <li>Oyunlar → TradeSim 3D</li>
                        <li>Şirketinizi oluşturun</li>
                        <li>Ürün/hizmet seçin</li>
                        <li>Alım-satım yapın</li>
                        <li>Finansal kararlar alın</li>
                        <li>Skorunuzu artırın</li>
                    </ol>
                    <div class="alert alert-success">
                        <strong>🎮 Eğlenceli Öğrenme:</strong> Gerçek mali kararlar, risk yok!
                    </div>
                ''',
                'related_topics': ['liderlik_tablosu', 'rozetler', 'seviye_atlama']
            }
        ],
        'quick_tips': [
            'İlk 100 kullanıcı özel rozet kazanır',
            'Liderlik tablosunda üst sıralara çıkın',
            'Günlük bonuslar için her gün giriş yapın',
        ]
    },
    
    # BLOCKCHAIN
    'blockchain': {
        'title': 'Blockchain Yardımı',
        'icon': 'bi-link-45deg',
        'sections': [
            {
                'title': 'Blockchain Nedir?',
                'content': '''
                    <h5>FinAsis'te Blockchain Kullanımı</h5>
                    <p>Blockchain, finansal kayıtlarınızın değiştirilemez ve şeffaf şekilde saklanmasını sağlar.</p>
                    <ul>
                        <li><strong>NFT Sertifikalar:</strong> Eğitim sertifikaları blockchain'de</li>
                        <li><strong>Başarı Rozetleri:</strong> Kalıcı ve transfer edilebilir</li>
                        <li><strong>Akıllı Sözleşmeler:</strong> Otomatik işlemler</li>
                        <li><strong>Denetim Kaydı:</strong> Tüm işlemler kalıcı</li>
                    </ul>
                ''',
                'related_topics': ['nft', 'smart_contracts', 'wallet']
            },
            {
                'title': 'NFT Cüzdan Bağlama',
                'content': '''
                    <h5>MetaMask Cüzdanınızı Nasıl Bağlarsınız?</h5>
                    <ol>
                        <li>Blockchain → Cüzdanlar sayfasına gidin</li>
                        <li>"Cüzdan Bağla" butonuna tıklayın</li>
                        <li>MetaMask eklentisini yükleyin (ilk kez ise)</li>
                        <li>MetaMask'tan bağlantı isteğini onaylayın</li>
                        <li>Cüzdan adresiniz görünecektir</li>
                    </ol>
                    <div class="alert alert-info">
                        <strong>💡 Not:</strong> NFT sertifikalarınız otomatik olarak bağlı cüzdanınıza gönderilir.
                    </div>
                ''',
                'related_topics': ['metamask', 'wallet', 'nft']
            }
        ],
        'quick_tips': [
            'Blockchain kayıtları silinemez ve değiştirilemez',
            'NFT\'lerinizi MetaMask cüzdanınıza alabilirsiniz',
            'Smart contract\'lar otomatik çalışır',
            'Tüm sertifikalar blockchain\'de kalıcı olarak saklanır',
        ],
        'shortcuts': [
            {'key': 'Alt+B', 'description': 'Blockchain Paneli'},
        ]
    },
    
    # DENETİM (AUDIT)
    'audit': {
        'title': 'Denetim Yardımı',
        'icon': 'bi-shield-check',
        'sections': [
            {
                'title': 'Denetim Logları',
                'content': '''
                    <h5>İşlem Kayıtlarını Nasıl Görüntülersiniz?</h5>
                    <ol>
                        <li>Denetim → Loglar sayfasına gidin</li>
                        <li>Filtreler ile tarih, kullanıcı veya işlem tipine göre arayın</li>
                        <li>Detaylı log için kayda tıklayın</li>
                        <li>Excel veya PDF olarak dışa aktarabilirsiniz</li>
                    </ol>
                    <div class="alert alert-success">
                        <strong>✓ Güvenlik:</strong> Tüm kritik işlemler otomatik loglanır.
                    </div>
                ''',
                'related_topics': ['loglar', 'guvenlik', 'takip']
            },
            {
                'title': 'Risk Değerlendirme',
                'content': '''
                    <h5>Finansal Risk Analizi Nasıl Yapılır?</h5>
                    <p>AI destekli risk analizi sistemi finansal durumunuzu değerlendirir.</p>
                    <ul>
                        <li><strong>Nakit Akış Riski:</strong> Gelecek 90 günlük nakit durumu</li>
                        <li><strong>Alacak Riski:</strong> Tahsilat gecikmeleri ve riskli müşteriler</li>
                        <li><strong>Bütçe Sapması:</strong> Planlanan vs gerçekleşen farkları</li>
                        <li><strong>Uyumluluk Kontrolü:</strong> Yasal gereksinimlerin karşılanması</li>
                    </ul>
                    <ol>
                        <li>Denetim → Risk Analizi sayfasına gidin</li>
                        <li>Dönem seçin ve "Analiz Et" tıklayın</li>
                        <li>Risk skorlarını ve önerileri inceleyin</li>
                        <li>Önerilen aksiyonları uygulayın</li>
                    </ol>
                ''',
                'related_topics': ['risk', 'analiz', 'uyumluluk']
            },
            {
                'title': 'Uyumluluk Raporları',
                'content': '''
                    <h5>Uyumluluk Kontrolleri</h5>
                    <p>FinAsis, KVKK, GDPR ve muhasebe standartlarına uygunluğu kontrol eder.</p>
                    <ul>
                        <li><strong>KVKK Kontrolü:</strong> Kişisel veri işleme uyumluluğu</li>
                        <li><strong>Muhasebe Standartları:</strong> TMS/TFRS uyumluluğu</li>
                        <li><strong>Vergi Uyumluluğu:</strong> Beyanname ve ödeme takibi</li>
                        <li><strong>Veri Güvenliği:</strong> Şifreleme ve erişim kontrolleri</li>
                    </ul>
                ''',
                'related_topics': ['kvkk', 'gdpr', 'uyumluluk']
            }
        ],
        'quick_tips': [
            'Tüm kritik işlemler otomatik loglanır',
            'Risk analizlerini düzenli olarak çalıştırın',
            'Uyumluluk raporlarını yasal danışmanınızla paylaşın',
            'AI destekli risk değerlendirmelerini takip edin',
        ],
        'shortcuts': [
            {'key': 'Alt+A', 'description': 'Denetim Paneli'},
            {'key': 'Alt+R', 'description': 'Risk Analizi'},
        ]
    },
    
    # FATURALAMA & ABONELİK (BILLING)
    'billing': {
        'title': 'Faturalama & Abonelik Yardımı',
        'icon': 'bi-credit-card',
        'sections': [
            {
                'title': 'Abonelik Yönetimi',
                'content': '''
                    <h5>Abonelik Planınızı Nasıl Yönetirsiniz?</h5>
                    <ol>
                        <li>Faturalama → Abonelik sayfasına gidin</li>
                        <li>Mevcut planınızı görüntüleyin</li>
                        <li>Plan değiştirmek için "Planı Değiştir" tıklayın</li>
                        <li>Yeni planı seçin ve ödeme bilgilerinizi güncelleyin</li>
                    </ol>
                    <div class="alert alert-info">
                        <strong>💡 Plan Türleri:</strong><br>
                        <strong>Starter:</strong> 1-5 kullanıcı, temel özellikler<br>
                        <strong>Pro:</strong> 6-20 kullanıcı, AI özellikleri, öncelikli destek<br>
                        <strong>Enterprise:</strong> Sınırsız kullanıcı, tüm özellikler, özel destek, özel entegrasyonlar
                    </div>
                ''',
                'related_topics': ['abonelik', 'plan', 'odeme']
            },
            {
                'title': 'Fatura ve Ödeme Geçmişi',
                'content': '''
                    <h5>Abonelik Faturalarını Nasıl Görüntülersiniz?</h5>
                    <ol>
                        <li>Faturalama → Faturalarım sayfasına gidin</li>
                        <li>Tüm abonelik faturalarınızı görüntüleyin</li>
                        <li>Faturaya tıklayarak detayları görebilirsiniz</li>
                        <li>PDF olarak indirebilir veya email ile paylaşabilirsiniz</li>
                    </ol>
                    <p><strong>Otomatik Ödemeler:</strong> Kredi kartı kayıtlıysa, ödemeler otomatik yapılır.</p>
                ''',
                'related_topics': ['fatura', 'odeme', 'gecmis']
            },
            {
                'title': 'Kullanım Limitleri',
                'content': '''
                    <h5>Abonelik Limitlerinizi Nasıl Kontrol Edersiniz?</h5>
                    <p>Her abonelik planının belirli limitleri vardır:</p>
                    <ul>
                        <li><strong>Kullanıcı Sayısı:</strong> Eş zamanlı kullanıcı limiti</li>
                        <li><strong>Depolama:</strong> Toplam veri depolama alanı</li>
                        <li><strong>API Çağrıları:</strong> Aylık API istek limiti</li>
                        <li><strong>AI Sorguları:</strong> AI Asistan kullanım limiti</li>
                    </ul>
                    <ol>
                        <li>Faturalama → Limitler sayfasına gidin</li>
                        <li>Kullanım durumunuzu görüntüleyin</li>
                        <li>Limitlere yaklaştığınızda uyarı alırsınız</li>
                        <li>Plan yükseltme önerileri otomatik sunulur</li>
                    </ol>
                ''',
                'related_topics': ['limit', 'kullanim', 'kot']
            }
        ],
        'quick_tips': [
            'Otomatik ödeme için kredi kartınızı kaydedin',
            'Fatura geçmişinizi düzenli olarak kontrol edin',
            'Kullanım limitlerinizi takip edin',
            'Plan değişiklikleri anında geçerli olur',
        ],
        'shortcuts': [
            {'key': 'Alt+C', 'description': 'Abonelik Merkezi'},
        ]
    },
    
    # MALİ MÜŞAVİRLİK (ADVISORS)
    'advisors': {
        'title': 'Mali Müşavirlik Yardımı',
        'icon': 'bi-briefcase',
        'sections': [
            {
                'title': 'Müşteri Yönetimi',
                'content': '''
                    <h5>Müşterilerinizi Nasıl Yönetirsiniz?</h5>
                    <ol>
                        <li>Mali Müşavirlik → Müşteriler sayfasına gidin</li>
                        <li>"Yeni Müşteri Ekle" butonuna tıklayın</li>
                        <li>Müşteri bilgilerini girin (şirket adı, vergi no, iletişim)</li>
                        <li>Yetkilendirmeleri ayarlayın (hangi verilere erişebileceği)</li>
                        <li>Müşteriyi kaydedin</li>
                    </ol>
                    <div class="alert alert-success">
                        <strong>✓ Çoklu Müşteri:</strong> Tüm müşterilerinizi tek panelden yönetebilirsiniz.
                    </div>
                ''',
                'related_topics': ['musteri', 'yetkilendirme', 'yonetim']
            },
            {
                'title': 'Danışmanlık Oturumları',
                'content': '''
                    <h5>Müşterilerinizle Nasıl Danışmanlık Oturumu Yaparsınız?</h5>
                    <ol>
                        <li>Müşteri profil sayfasına gidin</li>
                        <li>"Yeni Oturum" butonuna tıklayın</li>
                        <li>Oturum konusunu ve tarihini belirleyin</li>
                        <li>Toplantı linki otomatik oluşturulur (Zoom/Teams entegrasyonu)</li>
                        <li>Oturum notlarını kaydedin</li>
                        <li>Öneriler ve aksiyonlar belirleyin</li>
                    </ol>
                    <p><strong>Oturum Notları:</strong> Tüm danışmanlık oturumlarının kayıtları saklanır ve arama yapılabilir.</p>
                ''',
                'related_topics': ['oturum', 'danismanlik', 'toplanti']
            },
            {
                'title': 'Finansal Raporlama',
                'content': '''
                    <h5>Müşteriler İçin Rapor Nasıl Hazırlarsınız?</h5>
                    <ol>
                        <li>Müşteri → Raporlar sayfasına gidin</li>
                        <li>Rapor tipini seçin (Gelir Tablosu, Bilanço, Nakit Akışı, vb.)</li>
                        <li>Dönem seçin</li>
                        <li>Özelleştirme seçeneklerini ayarlayın</li>
                        <li>"Rapor Oluştur" tıklayın</li>
                        <li>PDF veya Excel olarak indirin veya müşteriye email gönderin</li>
                    </ol>
                    <div class="alert alert-info">
                        <strong>💡 Otomatik Raporlama:</strong> Düzenli raporlar için otomatik zamanlama ayarlayabilirsiniz.
                    </div>
                ''',
                'related_topics': ['rapor', 'finansal', 'musteri']
            },
            {
                'title': 'Marketplace - Hizmet Yönetimi',
                'content': '''
                    <h5>Mali Müşavirlik Hizmetlerinizi Nasıl Sunarsınız?</h5>
                    <p>FinAsis Marketplace üzerinden hizmetlerinizi sunabilirsiniz.</p>
                    <ol>
                        <li>Mali Müşavirlik → Marketplace → Hizmetlerim</li>
                        <li>"Yeni Hizmet Ekle" tıklayın</li>
                        <li>Hizmet bilgilerini girin (başlık, açıklama, fiyat)</li>
                        <li>Kategorileri ve etiketleri belirleyin</li>
                        <li>Hizmeti yayınla</li>
                    </ol>
                    <p><strong>Marketplace Avantajları:</strong> Potansiyel müşterilere ulaşın, hizmetlerinizi tanıtın ve sipariş alın.</p>
                ''',
                'related_topics': ['marketplace', 'hizmet', 'satin_alma']
            }
        ],
        'quick_tips': [
            'Müşteri verilerine erişim için mutlaka yetkilendirme yapın',
            'Danışmanlık oturumlarının notlarını düzenli tutun',
            'Otomatik raporlama ile zaman kazanın',
            'Marketplace\'de hizmetlerinizi tanıtın',
        ],
        'shortcuts': [
            {'key': 'Alt+M', 'description': 'Müşteri Yönetimi'},
            {'key': 'Alt+O', 'description': 'Yeni Oturum'},
        ]
    },
    
    # E-BELGE (EDOC)
    'edoc': {
        'title': 'eBelge Yardımı',
        'icon': 'bi-file-earmark-text',
        'sections': [
            {
                'title': 'e-Belge Yükleme',
                'content': '''
                    <h5>e-Belgeleri Nasıl Yüklersiniz?</h5>
                    <ol>
                        <li>eBelge → Belgeler sayfasına gidin</li>
                        <li>"Yeni Belge Yükle" butonuna tıklayın</li>
                        <li>Dosyayı seçin veya sürükle-bırak yapın</li>
                        <li>Belge tipini seçin (Fatura, Sözleşme, Makbuz, vb.)</li>
                        <li>OCR ile otomatik okuma için "Otomatik Oku" tıklayın</li>
                        <li>Kontrolleri yapın ve kaydedin</li>
                    </ol>
                    <div class="alert alert-info">
                        <strong>💡 OCR Desteği:</strong> AI ile belgeler otomatik okunur ve veriler çıkarılır.
                    </div>
                ''',
                'related_topics': ['yukleme', 'ocr', 'belge']
            },
            {
                'title': 'Belge Kategorileri ve Etiketleme',
                'content': '''
                    <h5>Belgeleri Nasıl Organize Edersiniz?</h5>
                    <p>Belgelerinizi kategorilere ayırarak düzenli tutabilirsiniz:</p>
                    <ul>
                        <li><strong>Kategoriler:</strong> Faturalar, Sözleşmeler, Faturalar, Makbuzlar, vb.</li>
                        <li><strong>Etiketler:</strong> Özel etiketler ekleyerek arama yapabilirsiniz</li>
                        <li><strong>Tarih Filtreleri:</strong> Belge tarihine göre filtreleme</li>
                        <li><strong>Müşteri/Tedarikçi:</strong> İlgili firma bazlı filtreleme</li>
                    </ul>
                ''',
                'related_topics': ['kategori', 'etiket', 'organizasyon']
            },
            {
                'title': 'Belge Arama ve Filtreleme',
                'content': '''
                    <h5>Belgelerinizi Nasıl Hızlıca Bulursunuz?</h5>
                    <ol>
                        <li>eBelge → Belgeler sayfasına gidin</li>
                        <li>Arama kutusuna anahtar kelime girin</li>
                        <li>Filtreleri kullanın (tarih, kategori, müşteri, vb.)</li>
                        <li>Gelişmiş arama için "Gelişmiş Filtreler" tıklayın</li>
                    </ol>
                    <p><strong>AI Arama:</strong> Belge içeriğindeki metinleri de arar (OCR ile okunan tüm belgeler).</p>
                ''',
                'related_topics': ['arama', 'filtre', 'bulma']
            }
        ],
        'quick_tips': [
            'OCR ile belgeleri otomatik okutun, manuel girişten kurtulun',
            'Belgeleri kategorilere ayırarak düzenli tutun',
            'Düzenli yedekleme için otomatik arşivleme kullanın',
            'Paylaşım linkleri ile belgeleri güvenli paylaşın',
        ],
        'shortcuts': [
            {'key': 'Alt+E', 'description': 'eBelge Paneli'},
            {'key': 'Ctrl+U', 'description': 'Belge Yükle'},
        ]
    },
    
    # KURUMSAL (CORPORATE)
    'corporate': {
        'title': 'Kurumsal Yönetim Yardımı',
        'icon': 'bi-building',
        'sections': [
            {
                'title': 'Şirket Bilgileri',
                'content': '''
                    <h5>Şirket Bilgilerinizi Nasıl Güncellersiniz?</h5>
                    <ol>
                        <li>Kurumsal → Şirket Bilgileri sayfasına gidin</li>
                        <li>Güncellenecek bilgileri düzenleyin</li>
                        <li>Logo ve görsel materyalleri yükleyin</li>
                        <li>Vergi bilgilerini kontrol edin</li>
                        <li>Değişiklikleri kaydedin</li>
                    </ol>
                    <div class="alert alert-warning">
                        <strong>⚠️ Dikkat:</strong> Vergi numarası ve mersis no değiştirilemez. Değişiklik için destek ile iletişime geçin.
                    </div>
                ''',
                'related_topics': ['sirket', 'bilgi', 'guncelleme']
            },
            {
                'title': 'Departman ve Takım Yönetimi',
                'content': '''
                    <h5>Organizasyon Yapınızı Nasıl Oluşturursunuz?</h5>
                    <ol>
                        <li>Kurumsal → Organizasyon sayfasına gidin</li>
                        <li>"Departman Ekle" ile departmanlar oluşturun</li>
                        <li>Kullanıcıları departmanlara atayın</li>
                        <li>Rol ve yetkileri belirleyin</li>
                        <li>Hiyerarşik yapıyı oluşturun (müdür, şef, vb.)</li>
                    </ol>
                    <p><strong>Organizasyon Şeması:</strong> Görsel organizasyon şeması otomatik oluşturulur.</p>
                ''',
                'related_topics': ['departman', 'organizasyon', 'takim']
            }
        ],
        'quick_tips': [
            'Şirket logo ve görsellerini yükleyerek profesyonel görünüm sağlayın',
            'Organizasyon yapısını düzenli tutun',
            'Departman bazlı raporlama yapabilirsiniz',
        ],
    },
    
    # YÖNETİM (MANAGEMENT) - ADMIN
    'management': {
        'title': 'Yönetim Paneli Yardımı',
        'icon': 'bi-gear',
        'sections': [
            {
                'title': 'Kullanıcı Yönetimi',
                'content': '''
                    <h5>Kullanıcıları Nasıl Yönetirsiniz?</h5>
                    <ol>
                        <li>Yönetim → Kullanıcılar sayfasına gidin</li>
                        <li>"Yeni Kullanıcı Ekle" butonuna tıklayın</li>
                        <li>Kullanıcı bilgilerini girin</li>
                        <li>Rol ve yetkileri atayın</li>
                        <li>E-posta davetiyesi gönderin</li>
                    </ol>
                    <div class="alert alert-success">
                        <strong>✓ Toplu İşlem:</strong> Excel ile toplu kullanıcı ekleme desteklenir.
                    </div>
                ''',
                'related_topics': ['kullanici', 'rol', 'yetki']
            },
            {
                'title': 'Rol ve Yetki Yönetimi',
                'content': '''
                    <h5>Rolleri Nasıl Özelleştirirsiniz?</h5>
                    <ol>
                        <li>Yönetim → Roller sayfasına gidin</li>
                        <li>Mevcut rolleri görüntüleyin veya yeni rol oluşturun</li>
                        <li>İzinleri seçin (okuma, yazma, silme, onaylama)</li>
                        <li>Modül bazlı yetkilendirme yapın</li>
                        <li>Rolü kaydedin</li>
                    </ol>
                    <p><strong>Özel Roller:</strong> İhtiyacınıza göre özel roller oluşturabilirsiniz.</p>
                ''',
                'related_topics': ['rol', 'yetki', 'izin']
            },
            {
                'title': 'Sistem Ayarları',
                'content': '''
                    <h5>Sistem Genel Ayarlarını Nasıl Yapılandırırsınız?</h5>
                    <ol>
                        <li>Yönetim → Ayarlar sayfasına gidin</li>
                        <li>Genel ayarları düzenleyin (şirket adı, para birimi, dil, vb.)</li>
                        <li>E-posta ayarlarını yapılandırın</li>
                        <li>Entegrasyon ayarlarını kontrol edin (e-Fatura, banka, vb.)</li>
                        <li>Güvenlik ayarlarını yapın (2FA, şifre politikası, vb.)</li>
                        <li>Değişiklikleri kaydedin</li>
                    </ol>
                    <div class="alert alert-warning">
                        <strong>⚠️ Önemli:</strong> Sistem ayarları tüm kullanıcıları etkiler. Değişiklik yapmadan önce dikkatli olun.
                    </div>
                ''',
                'related_topics': ['ayar', 'sistem', 'yapilandirma']
            },
            {
                'title': 'Sistem İstatistikleri',
                'content': '''
                    <h5>Sistem Kullanım İstatistiklerini Nasıl Görüntülersiniz?</h5>
                    <ol>
                        <li>Yönetim → İstatistikler sayfasına gidin</li>
                        <li>Aktif kullanıcı sayısını görüntüleyin</li>
                        <li>Modül kullanım istatistiklerini inceleyin</li>
                        <li>Veri kullanım raporlarını görüntüleyin</li>
                        <li>Performans metriklerini takip edin</li>
                    </ol>
                ''',
                'related_topics': ['istatistik', 'rapor', 'performans']
            }
        ],
        'quick_tips': [
            'Düzenli olarak kullanıcı erişimlerini gözden geçirin',
            'Rol ve yetkileri düzenli olarak güncelleyin',
            'Sistem yedeklemelerini kontrol edin',
            'Güvenlik loglarını düzenli inceleyin',
        ],
        'shortcuts': [
            {'key': 'Alt+G', 'description': 'Yönetim Paneli'},
            {'key': 'Alt+U', 'description': 'Kullanıcı Yönetimi'},
        ]
    },
    
    # KULLANICI YÖNETİMİ (ACCOUNTS)
    'accounts': {
        'title': 'Kullanıcı & Profil Yardımı',
        'icon': 'bi-person',
        'sections': [
            {
                'title': 'Profil Ayarları',
                'content': '''
                    <h5>Profil Bilgilerinizi Nasıl Güncellersiniz?</h5>
                    <ol>
                        <li>Sağ üst köşedeki profil ikonuna tıklayın</li>
                        <li>"Profil" seçeneğini seçin</li>
                        <li>Kişisel bilgilerinizi güncelleyin (ad, soyad, e-posta, telefon)</li>
                        <li>Profil fotoğrafı yükleyin</li>
                        <li>Dil ve saat dilimi tercihlerinizi ayarlayın</li>
                        <li>Değişiklikleri kaydedin</li>
                    </ol>
                ''',
                'related_topics': ['profil', 'ayar', 'guncelleme']
            },
            {
                'title': 'Şifre Değiştirme',
                'content': '''
                    <h5>Şifrenizi Nasıl Değiştirirsiniz?</h5>
                    <ol>
                        <li>Profil → Güvenlik sayfasına gidin</li>
                        <li>"Şifre Değiştir" butonuna tıklayın</li>
                        <li>Mevcut şifrenizi girin</li>
                        <li>Yeni şifrenizi girin (en az 8 karakter, harf ve rakam)</li>
                        <li>Yeni şifrenizi tekrar girin</li>
                        <li>"Değiştir" butonuna tıklayın</li>
                    </ol>
                    <div class="alert alert-warning">
                        <strong>⚠️ Güvenlik:</strong> Güçlü şifre kullanın ve düzenli olarak değiştirin.
                    </div>
                ''',
                'related_topics': ['sifre', 'guvenlik', 'degistirme']
            },
            {
                'title': 'İki Faktörlü Doğrulama (2FA)',
                'content': '''
                    <h5>2FA Nasıl Aktif Edilir?</h5>
                    <ol>
                        <li>Profil → Güvenlik sayfasına gidin</li>
                        <li>"İki Faktörlü Doğrulama" bölümüne gidin</li>
                        <li>"2FA'yı Aktif Et" butonuna tıklayın</li>
                        <li>QR kodu Google Authenticator veya benzeri bir uygulama ile tarayın</li>
                        <li>Doğrulama kodunu girin</li>
                        <li>Yedek kurtarma kodlarını kaydedin</li>
                    </ol>
                    <div class="alert alert-success">
                        <strong>✓ Güvenlik Artışı:</strong> 2FA hesabınızın güvenliğini önemli ölçüde artırır.
                    </div>
                ''',
                'related_topics': ['2fa', 'guvenlik', 'dogrulama']
            },
            {
                'title': 'Bildirim Tercihleri',
                'content': '''
                    <h5>Bildirim Ayarlarını Nasıl Yapılandırırsınız?</h5>
                    <ol>
                        <li>Profil → Bildirimler sayfasına gidin</li>
                        <li>E-posta bildirimlerini aktif/pasif yapın</li>
                        <li>SMS bildirimlerini ayarlayın (opsiyonel)</li>
                        <li>Push bildirimlerini yönetin</li>
                        <li>Bildirim türlerini seçin (fatura, ödeme, rapor, vb.)</li>
                        <li>Tercihleri kaydedin</li>
                    </ol>
                ''',
                'related_topics': ['bildirim', 'eposta', 'tercih']
            }
        ],
        'quick_tips': [
            'Profil fotoğrafı ekleyerek hesabınızı kişiselleştirin',
            'Güçlü ve benzersiz şifre kullanın',
            '2FA\'yı mutlaka aktif edin',
            'Bildirim tercihlerinizi ihtiyacınıza göre ayarlayın',
        ],
        'shortcuts': [
            {'key': 'Alt+P', 'description': 'Profil Ayarları'},
        ]
    },
}

# ============================================================================
# HIZLI İPUÇLARI (QUICK TIPS)
# ============================================================================

QUICK_TIPS = {
    'dashboard': [
        'Dashboard\'unuzu özelleştirmek için widget\'ları sürükleyip bırakın',
        'KPI kartlarına tıklayarak detaylı rapor alabilirsiniz',
        'Filtreleri kullanarak dönem bazlı analiz yapın',
    ],
    'invoice': [
        'Fatura şablonları kullanarak hızlı fatura oluşturun',
        'Toplu fatura import için Excel kullanın',
        'AI Asistan ile sesli fatura oluşturun',
        'QR kod ile faturalarınızı paylaşın',
    ],
    'payment': [
        'Ödeme hatırlatıcıları otomatik email gönderir',
        'Taksitli ödemeleri takip edebilirsiniz',
        'Banka entegrasyonu ile otomatik mutabakat',
    ],
    'reporting': [
        'Raporlar PDF, Excel veya email olarak alınabilir',
        'Otomatik raporlama ayarlayabilirsiniz',
        'Özel rapor tasarlayabilirsiniz',
    ],
}

# ============================================================================
# KLAVYE KISAYOLLARI (KEYBOARD SHORTCUTS)
# ============================================================================

KEYBOARD_SHORTCUTS = {
    'global': [
        {'key': 'Alt+D', 'description': 'Dashboard\'a git', 'category': 'Gezinme'},
        {'key': 'Alt+S', 'description': 'Arama', 'category': 'Gezinme'},
        {'key': 'Alt+H', 'description': 'Yardım', 'category': 'Gezinme'},
        {'key': 'Ctrl+K', 'description': 'Komut paleti', 'category': 'Gezinme'},
        {'key': 'Esc', 'description': 'Modal\'ı kapat', 'category': 'Gezinme'},
    ],
    'accounting': [
        {'key': 'Alt+F', 'description': 'Yeni Fatura', 'category': 'Muhasebe'},
        {'key': 'Alt+M', 'description': 'Mizan Raporu', 'category': 'Muhasebe'},
        {'key': 'Alt+Y', 'description': 'Yevmiye Defteri', 'category': 'Muhasebe'},
        {'key': 'Ctrl+Enter', 'description': 'Fişi Onayla', 'category': 'Muhasebe'},
    ],
    'finance': [
        {'key': 'Alt+B', 'description': 'Banka Hareketleri', 'category': 'Finans'},
        {'key': 'Alt+P', 'description': 'Ödeme Yap', 'category': 'Finans'},
        {'key': 'Alt+T', 'description': 'Tahsilat', 'category': 'Finans'},
        {'key': 'Alt+K', 'description': 'KPI Dashboard', 'category': 'Finans'},
    ],
    'ai_assistant': [
        {'key': 'Alt+AI', 'description': 'AI Asistan Aç', 'category': 'AI'},
        {'key': 'Ctrl+M', 'description': 'Mikrofon Aktif/Pasif', 'category': 'AI'},
        {'key': 'Alt+O', 'description': 'OCR Belge Oku', 'category': 'AI'},
    ],
    'education': [
        {'key': 'Alt+E', 'description': 'Eğitim Merkezi', 'category': 'Eğitim'},
        {'key': 'Alt+Q', 'description': 'FinQuest', 'category': 'Eğitim'},
    ],
    'games': [
        {'key': 'Alt+G', 'description': 'Oyunlar', 'category': 'Oyun'},
        {'key': 'Alt+TS', 'description': 'TradeSim 3D', 'category': 'Oyun'},
    ],
}

# ============================================================================
# SSS (FAQ)
# ============================================================================

FAQ_CATEGORIES = {
    'baslangic': {
        'title': 'Başlangıç',
        'icon': 'bi-play-circle',
        'questions': [
            {
                'question': 'FinAsis nedir?',
                'answer': '''
                    FinAsis, KOBİ'ler için yapay zeka destekli finansal yönetim ve muhasebe platformudur.
                    Muhasebe, finans, eğitim ve oyun modüllerini tek platformda sunar.
                ''',
                'tags': ['genel', 'tanitim']
            },
            {
                'question': 'Nasıl başlarım?',
                'answer': '''
                    1. Hesap oluşturun veya giriş yapın
                    2. Şirket bilgilerinizi tamamlayın
                    3. Dashboard'u inceleyin
                    4. Hızlı Başlangıç turunu tamamlayın
                    5. İlk faturanızı oluşturun
                ''',
                'tags': ['baslangic', 'setup']
            },
            {
                'question': 'Hangi abonelik paketini seçmeliyim?',
                'answer': '''
                    <strong>Starter:</strong> 1-5 kullanıcı, temel özellikler
                    <strong>Pro:</strong> 6-20 kullanıcı, AI özellikleri
                    <strong>Enterprise:</strong> Sınırsız kullanıcı, tüm özellikler, özel destek
                ''',
                'tags': ['abonelik', 'fiyatlandirma']
            }
        ]
    },
    'muhasebe': {
        'title': 'Muhasebe',
        'icon': 'bi-calculator',
        'questions': [
            {
                'question': 'Fatura nasıl oluşturulur?',
                'answer': 'Muhasebe → Faturalar → Yeni Fatura. Detaylı rehber için Yardım → Muhasebe bölümüne bakın.',
                'tags': ['fatura', 'satis']
            },
            {
                'question': 'Otomatik fiş kesme nasıl çalışır?',
                'answer': '''
                    Fatura oluşturduğunuzda, sistem otomatik olarak muhasebe fişini keser.
                    Hesap planına göre borç/alacak kayıtları yapılır. KDV otomatik hesaplanır.
                ''',
                'tags': ['fis', 'otomasyon']
            },
            {
                'question': 'e-Fatura nasıl gönderilir?',
                'answer': '''
                    Fatura oluşturduktan sonra "e-Fatura Gönder" butonuna tıklayın.
                    Sistem GİB'e otomatik gönderir. e-Arşiv fatura da desteklenir.
                ''',
                'tags': ['e-fatura', 'gib']
            },
            {
                'question': 'KDV beyannamesi nasıl hazırlanır?',
                'answer': '''
                    Muhasebe → Beyannameler → KDV. Sistem otomatik hesaplar, sadece kontrol edip gönderin.
                ''',
                'tags': ['kdv', 'beyanname']
            }
        ]
    },
    'guvenlik': {
        'title': 'Güvenlik',
        'icon': 'bi-shield-check',
        'questions': [
            {
                'question': 'Verilerim güvende mi?',
                'answer': '''
                    Evet! FinAsis çok katmanlı güvenlik kullanır:
                    - Tüm veriler şifrelenmiş saklanır
                    - SSL/HTTPS ile güvenli bağlantı
                    - 2FA (İki faktörlü doğrulama) desteği
                    - KVKK/GDPR uyumlu
                    - Blockchain ile değiştirilemez kayıtlar
                ''',
                'tags': ['guvenlik', 'gizlilik']
            },
            {
                'question': 'AI verilerimi dışarı gönderir mi?',
                'answer': '''
                    HAYIR! FinAsis'teki AI tamamen yerelde çalışır (local AI).
                    Verileriniz asla dışarı çıkmaz. Gizlilik odaklı tasarım.
                ''',
                'tags': ['ai', 'gizlilik']
            }
        ]
    },
    'teknik': {
        'title': 'Teknik',
        'icon': 'bi-gear',
        'questions': [
            {
                'question': 'Hangi tarayıcıları destekler?',
                'answer': 'Chrome, Firefox, Safari, Edge (son 2 versiyon). IE desteklenmez.',
                'tags': ['tarayici', 'teknik']
            },
            {
                'question': 'Mobil uygulama var mı?',
                'answer': '''
                    FinAsis PWA (Progressive Web App) olarak çalışır.
                    Mobil tarayıcınızdan "Ana Ekrana Ekle" ile uygulama gibi kullanabilirsiniz.
                    Yakında iOS ve Android native app gelecek.
                ''',
                'tags': ['mobil', 'pwa']
            },
            {
                'question': 'Offline çalışır mı?',
                'answer': '''
                    Kısıtlı offline destek var. Temel özellikler offline kullanılabilir,
                    sync olduğunda veriler sunucuya gönderilir.
                ''',
                'tags': ['offline', 'pwa']
            },
            {
                'question': 'API entegrasyonu var mı?',
                'answer': '''
                    Evet! FinAsis REST API desteği sunar. API dokümantasyonu için Developer Portal'ı ziyaret edin.
                    API key'lerinizi profil ayarlarından oluşturabilirsiniz.
                ''',
                'tags': ['api', 'entegrasyon', 'teknik']
            },
            {
                'question': 'Veri yedekleme nasıl yapılır?',
                'answer': '''
                    Tüm verileriniz otomatik yedeklenir. Manuel yedekleme için:
                    Yönetim → Ayarlar → Yedekleme → Manuel Yedekleme.
                    Excel veya PDF formatında veri dışa aktarımı da mevcuttur.
                ''',
                'tags': ['yedekleme', 'veri', 'guvenlik']
            }
        ]
    },
    'denetim': {
        'title': 'Denetim',
        'icon': 'bi-shield-check',
        'questions': [
            {
                'question': 'Denetim logları ne kadar süre saklanır?',
                'answer': '''
                    Kritik işlem logları 7 yıl saklanır (yasal gereksinim). 
                    Genel loglar 2 yıl saklanır. Daha uzun süre için arşivleme özelliğini kullanabilirsiniz.
                ''',
                'tags': ['log', 'denetim', 'saklama']
            },
            {
                'question': 'Risk analizi nasıl çalışır?',
                'answer': '''
                    AI destekli risk analizi sistemi, finansal verilerinizi analiz eder ve risk skorları oluşturur.
                    Nakit akışı, alacak, bütçe sapması ve uyumluluk risklerini değerlendirir.
                    Haftalık veya aylık otomatik analiz çalıştırabilirsiniz.
                ''',
                'tags': ['risk', 'analiz', 'ai']
            },
            {
                'question': 'Uyumluluk raporları neler içerir?',
                'answer': '''
                    KVKK uyumluluğu, GDPR uyumluluğu, muhasebe standartları (TMS/TFRS), 
                    vergi uyumluluğu ve veri güvenliği kontrolleri içerir.
                    Raporlar PDF olarak indirilebilir ve yasal danışmanınızla paylaşılabilir.
                ''',
                'tags': ['uyumluluk', 'rapor', 'kvkk']
            }
        ]
    },
    'faturalama': {
        'title': 'Faturalama & Abonelik',
        'icon': 'bi-credit-card',
        'questions': [
            {
                'question': 'Abonelik planımı nasıl değiştiririm?',
                'answer': '''
                    Faturalama → Abonelik sayfasından mevcut planınızı görüntüleyin ve "Planı Değiştir" tıklayın.
                    Plan değişiklikleri anında geçerli olur. Yeni plan farkı bir sonraki faturada yansır.
                ''',
                'tags': ['abonelik', 'plan', 'degistirme']
            },
            {
                'question': 'Otomatik ödeme nasıl ayarlanır?',
                'answer': '''
                    Faturalama → Ödeme Yöntemleri → Kredi Kartı Ekle.
                    Kart bilgilerinizi güvenli şekilde kaydedin. Ödemeler otomatik yapılır.
                    Her ödeme öncesi email bildirimi gönderilir.
                ''',
                'tags': ['odeme', 'kart', 'otomatik']
            },
            {
                'question': 'Kullanım limitime nasıl bakabilirim?',
                'answer': '''
                    Faturalama → Limitler sayfasından mevcut kullanımınızı ve limitlerinizi görüntüleyebilirsiniz.
                    Limitlere yaklaştığınızda uyarı email'i gönderilir.
                    Plan yükseltme önerileri otomatik sunulur.
                ''',
                'tags': ['limit', 'kullanim', 'kot']
            }
        ]
    },
    'mali_musavir': {
        'title': 'Mali Müşavirlik',
        'icon': 'bi-briefcase',
        'questions': [
            {
                'question': 'Müşteri eklemek için ne gerekiyor?',
                'answer': '''
                    Mali Müşavirlik → Müşteriler → Yeni Müşteri Ekle.
                    Müşteri bilgilerini girin ve yetkilendirmeleri ayarlayın.
                    Müşteri kendi hesabına giriş yapabilir ve size yetkilendirilmiş verileri görebilir.
                ''',
                'tags': ['musteri', 'ekleme', 'yetkilendirme']
            },
            {
                'question': 'Marketplace\'de hizmet nasıl sunulur?',
                'answer': '''
                    Mali Müşavirlik → Marketplace → Hizmetlerim → Yeni Hizmet Ekle.
                    Hizmet bilgilerini girin (başlık, açıklama, fiyat, kategori).
                    Hizmeti yayınlayın. Potansiyel müşteriler hizmetinizi görüntüleyebilir ve sipariş verebilir.
                ''',
                'tags': ['marketplace', 'hizmet', 'satin_alma']
            },
            {
                'question': 'Müşteri raporları nasıl hazırlanır?',
                'answer': '''
                    Müşteri profil sayfasından → Raporlar → Rapor Tipi Seç → Dönem Belirle → Oluştur.
                    PDF veya Excel olarak indirebilir veya müşteriye email ile gönderebilirsiniz.
                    Otomatik raporlama için zamanlama ayarlayabilirsiniz.
                ''',
                'tags': ['rapor', 'musteri', 'otomatik']
            }
        ]
    },
    'egitim': {
        'title': 'Eğitim',
        'icon': 'bi-mortarboard',
        'questions': [
            {
                'question': 'Derslere nasıl kayıt olunur?',
                'answer': '''
                    Eğitim → Dersler sayfasından ilginizi çeken kursu seçin ve "Kursa Kayıt Ol" tıklayın.
                    Bazı dersler ücretsiz, bazıları ücretli olabilir.
                    Kayıt olduktan sonra ders materyallerine erişebilirsiniz.
                ''',
                'tags': ['ders', 'kayit', 'kurs']
            },
            {
                'question': 'FinQuest nedir?',
                'answer': '''
                    FinQuest, görev bazlı öğrenme sistemidir. Finansal okuryazarlığınızı artırmak için 
                    görevleri tamamlayarak puan ve rozetler kazanırsınız.
                    Eğitim → FinQuest sayfasından görevleri görüntüleyebilirsiniz.
                ''',
                'tags': ['finquest', 'gorev', 'oyun']
            },
            {
                'question': 'Sertifikalar NFT olarak nasıl alınır?',
                'answer': '''
                    Kursu tamamladığınızda sertifika otomatik oluşturulur ve blockchain'e kaydedilir.
                    Blockchain → Cüzdanlar sayfasından MetaMask cüzdanınızı bağlayın.
                    Sertifikalar otomatik olarak cüzdanınıza gönderilir (NFT olarak).
                ''',
                'tags': ['sertifika', 'nft', 'blockchain']
            },
            {
                'question': 'Öğretmen olarak nasıl ders oluştururum?',
                'answer': '''
                    Öğretmen rolüne sahipseniz: Eğitim → Öğretmen Paneli → Derslerim → Yeni Ders Oluştur.
                    Ders bilgilerini, video ve materyalleri, quiz sorularını ekleyin ve dersi yayınlayın.
                    Öğrenci ilerlemelerini takip edebilirsiniz.
                ''',
                'tags': ['ogretmen', 'ders', 'olusturma']
            }
        ]
    },
    'oyunlar': {
        'title': 'Oyunlar',
        'icon': 'bi-controller',
        'questions': [
            {
                'question': 'TradeSim 3D nasıl oynanır?',
                'answer': '''
                    Oyunlar → TradeSim 3D sayfasına gidin. İlk kez oynuyorsanız şirketinizi oluşturun.
                    Ürün/hizmet seçin, alım-satım yapın, finansal kararlar alın.
                    Gerçek mali kararlar, risk yok! Skorunuzu artırın ve liderlik tablosunda yer alın.
                ''',
                'tags': ['tradesim', 'oyun', 'simulasyon']
            },
            {
                'question': 'Liderlik tablosu nedir?',
                'answer': '''
                    TradeSim oyununda en yüksek skorlu kullanıcılar liderlik tablosunda görüntülenir.
                    Üst sıralara çıkmak için iyi finansal kararlar alın, şirketinizi büyütün.
                    Aylık ve toplam skor tabloları mevcuttur.
                ''',
                'tags': ['liderlik', 'skor', 'tablo']
            },
            {
                'question': 'Oyun rozetleri nelerdir?',
                'answer': '''
                    Görevleri tamamlayarak, başarılar elde ederek rozetler kazanabilirsiniz.
                    Örnek: "İlk 100 kullanıcı", "Haftalık Şampiyon", "Ciro Kralı", vb.
                    Rozetler blockchain'de NFT olarak saklanır ve cüzdanınıza gönderilir.
                ''',
                'tags': ['rozet', 'basari', 'nft']
            }
        ]
    },
    'blockchain': {
        'title': 'Blockchain',
        'icon': 'bi-link-45deg',
        'questions': [
            {
                'question': 'NFT cüzdanı nasıl bağlanır?',
                'answer': '''
                    Blockchain → Cüzdanlar → Cüzdan Bağla.
                    MetaMask eklentisini yükleyin (ilk kez ise) ve bağlantı isteğini onaylayın.
                    Cüzdan adresiniz görünecek ve NFT sertifikalar/rozetler otomatik gönderilecek.
                ''',
                'tags': ['cuzdan', 'metamask', 'nft']
            },
            {
                'question': 'Blockchain kayıtları değiştirilebilir mi?',
                'answer': '''
                    HAYIR! Blockchain kayıtları silinemez ve değiştirilemez. 
                    Bu, tüm finansal işlemlerin ve sertifikaların kalıcı ve güvenilir olmasını sağlar.
                    Akıllı sözleşmeler otomatik çalışır.
                ''',
                'tags': ['blockchain', 'kalici', 'guvenlik']
            },
            {
                'question': 'NFT\'lerimi başka bir cüzdana transfer edebilir miyim?',
                'answer': '''
                    Evet! NFT sertifikalar ve rozetler transfer edilebilir dijital varlıklardır.
                    MetaMask cüzdanınızdan başka bir cüzdana gönderebilirsiniz.
                    Ancak eğitim sertifikaları genellikle transfer edilemez şekilde oluşturulur (güvenlik için).
                ''',
                'tags': ['nft', 'transfer', 'cuzdan']
            }
        ]
    }
}

# ============================================================================
# GUIDED TOUR (Rehberli Tur)
# ============================================================================

GUIDED_TOURS = {
    'first_time_user': {
        'title': 'İlk Kez Kullanıyorum',
        'steps': [
            {
                'target': '#dashboard',
                'title': 'Hoş Geldiniz! 👋',
                'content': 'Bu Dashboard\'unuz. Tüm önemli bilgileri buradan görürsünüz.',
                'position': 'bottom'
            },
            {
                'target': '#sidebar-menu',
                'title': 'Ana Menü',
                'content': 'Sol taraftaki menüden tüm modüllere erişebilirsiniz.',
                'position': 'right'
            },
            {
                'target': '#quick-actions',
                'title': 'Hızlı İşlemler',
                'content': 'En sık kullanılan işlemleri buradan hızlıca yapabilirsiniz.',
                'position': 'bottom'
            },
            {
                'target': '#ai-assistant-btn',
                'title': 'AI Asistan 🤖',
                'content': 'Sesli veya yazılı komutlarla AI Asistan\'dan yardım alabilirsiniz.',
                'position': 'left'
            },
            {
                'target': '#notifications',
                'title': 'Bildirimler 🔔',
                'content': 'Önemli olaylar için bildirim alırsınız.',
                'position': 'bottom'
            },
        ]
    },
    'accounting_tour': {
        'title': 'Muhasebe Modülü Turu',
        'steps': [
            {
                'target': '#invoice-list',
                'title': 'Faturalar',
                'content': 'Tüm faturalarınızı burada görürsünüz.',
                'position': 'top'
            },
            {
                'target': '#new-invoice-btn',
                'title': 'Yeni Fatura',
                'content': 'Buradan yeni fatura oluşturabilirsiniz.',
                'position': 'bottom'
            },
            {
                'target': '#voucher-list',
                'title': 'Muhasebe Fişleri',
                'content': 'Otomatik oluşturulan fişleri burada görürsünüz.',
                'position': 'top'
            },
        ]
    }
}

# ============================================================================
# TOOLTIP METİNLERİ
# ============================================================================

TOOLTIPS = {
    # Genel
    'save_button': 'Değişiklikleri kaydet (Ctrl+S)',
    'cancel_button': 'İptal et ve geri dön (Esc)',
    'delete_button': 'Kalıcı olarak sil - Bu işlem geri alınamaz!',
    'approve_button': 'Onayla - Onaylanan kayıtlar değiştirilemez',
    
    # Muhasebe
    'invoice_number': 'Fatura numarası otomatik oluşturulur',
    'tax_rate': 'KDV oranı (varsayılan %20). Değiştirebilirsiniz.',
    'due_date': 'Ödeme vadesi. Hatırlatıcı email gönderilir.',
    'auto_voucher': 'Otomatik muhasebe fişi kesilecek',
    
    # Finans
    'cash_flow': 'Giriş ve çıkışların net farkı',
    'bank_balance': 'Gerçek zamanlı banka bakiyesi',
    'payment_status': 'Ödeme durumu: Beklemede, Ödendi, Gecikmiş',
    
    # AI
    'ai_voice': 'Mikrofona tıklayın ve komutunuzu söyleyin',
    'ai_privacy': 'Verileriniz dışarı çıkmaz. Tam gizlilik.',
    'ocr_upload': 'Belge fotoğrafı yükleyin, AI otomatik okur',
}

# ============================================================================
# VİDEO TUTORİAL LİSTESİ
# ============================================================================

VIDEO_TUTORIALS = {
    'accounting': [
        {
            'title': 'İlk Faturanızı Oluşturun',
            'duration': '3:45',
            'thumbnail': '/static/help/thumbs/fatura-olusturma.jpg',
            'video_url': '/help/videos/fatura-olusturma.mp4',
            'description': 'Adım adım fatura oluşturma rehberi',
            'level': 'Başlangıç'
        },
        {
            'title': 'Otomatik Fiş Kesme Sistemi',
            'duration': '5:20',
            'thumbnail': '/static/help/thumbs/fis-kesme.jpg',
            'video_url': '/help/videos/fis-kesme.mp4',
            'description': 'Otomatik muhasebe fişi nasıl çalışır',
            'level': 'Orta'
        },
        {
            'title': 'e-Fatura Gönderimi',
            'duration': '4:15',
            'thumbnail': '/static/help/thumbs/e-fatura.jpg',
            'video_url': '/help/videos/e-fatura.mp4',
            'description': 'GİB\'e e-Fatura nasıl gönderilir',
            'level': 'Orta'
        },
    ],
    'ai_assistant': [
        {
            'title': 'AI Asistan ile Sesli Komut',
            'duration': '2:30',
            'thumbnail': '/static/help/thumbs/sesli-komut.jpg',
            'video_url': '/help/videos/sesli-komut.mp4',
            'description': 'Sesli komutla fatura oluşturma',
            'level': 'Başlangıç'
        },
        {
            'title': 'OCR ile Belge Okuma',
            'duration': '3:00',
            'thumbnail': '/static/help/thumbs/ocr.jpg',
            'video_url': '/help/videos/ocr-belge-okuma.mp4',
            'description': 'Fatura fotoğrafını otomatik okutma',
            'level': 'Başlangıç'
        },
    ],
    'games': [
        {
            'title': 'TradeSim 3D\'ye Başlangıç',
            'duration': '6:00',
            'thumbnail': '/static/help/thumbs/tradesim-baslangic.jpg',
            'video_url': '/help/videos/tradesim-baslangic.mp4',
            'description': 'İlk şirketinizi kurun ve ticarete başlayın',
            'level': 'Başlangıç'
        },
    ],
    'finance': [
        {
            'title': 'KPI Dashboard Kullanımı',
            'duration': '4:30',
            'thumbnail': '/static/help/thumbs/kpi-dashboard.jpg',
            'video_url': '/help/videos/kpi-dashboard.mp4',
            'description': 'Finansal KPI\'ları nasıl takip edersiniz',
            'level': 'Orta'
        },
        {
            'title': 'Bütçe Planlama',
            'duration': '5:00',
            'thumbnail': '/static/help/thumbs/butce-planlama.jpg',
            'video_url': '/help/videos/butce-planlama.mp4',
            'description': 'Bütçe oluşturma ve takip etme',
            'level': 'Orta'
        },
        {
            'title': 'Banka Entegrasyonu',
            'duration': '6:15',
            'thumbnail': '/static/help/thumbs/banka-entegrasyon.jpg',
            'video_url': '/help/videos/banka-entegrasyon.mp4',
            'description': 'Banka hesaplarınızı nasıl bağlarsınız',
            'level': 'İleri'
        },
    ],
    'audit': [
        {
            'title': 'Risk Analizi Yapma',
            'duration': '5:45',
            'thumbnail': '/static/help/thumbs/risk-analiz.jpg',
            'video_url': '/help/videos/risk-analiz.mp4',
            'description': 'AI destekli finansal risk analizi',
            'level': 'İleri'
        },
        {
            'title': 'Denetim Logları',
            'duration': '3:30',
            'thumbnail': '/static/help/thumbs/denetim-log.jpg',
            'video_url': '/help/videos/denetim-log.mp4',
            'description': 'İşlem kayıtlarını görüntüleme ve filtreleme',
            'level': 'Orta'
        },
    ],
    'education': [
        {
            'title': 'FinQuest Görev Sistemi',
            'duration': '4:00',
            'thumbnail': '/static/help/thumbs/finquest.jpg',
            'video_url': '/help/videos/finquest.mp4',
            'description': 'Görev bazlı öğrenme sistemi',
            'level': 'Başlangıç'
        },
        {
            'title': 'Ders Oluşturma (Öğretmenler)',
            'duration': '7:30',
            'thumbnail': '/static/help/thumbs/ders-olusturma.jpg',
            'video_url': '/help/videos/ders-olusturma.mp4',
            'description': 'Öğretmenler için ders oluşturma rehberi',
            'level': 'Orta'
        },
    ],
    'billing': [
        {
            'title': 'Abonelik Planı Değiştirme',
            'duration': '3:00',
            'thumbnail': '/static/help/thumbs/plan-degistirme.jpg',
            'video_url': '/help/videos/plan-degistirme.mp4',
            'description': 'Abonelik planınızı nasıl değiştirirsiniz',
            'level': 'Başlangıç'
        },
    ],
    'advisors': [
        {
            'title': 'Müşteri Yönetimi',
            'duration': '5:00',
            'thumbnail': '/static/help/thumbs/musteri-yonetim.jpg',
            'video_url': '/help/videos/musteri-yonetim.mp4',
            'description': 'Mali müşavirler için müşteri yönetimi',
            'level': 'Orta'
        },
        {
            'title': 'Marketplace Hizmet Sunumu',
            'duration': '4:30',
            'thumbnail': '/static/help/thumbs/marketplace.jpg',
            'video_url': '/help/videos/marketplace.mp4',
            'description': 'Marketplace\'de hizmet nasıl sunulur',
            'level': 'Orta'
        },
    ],
    'blockchain': [
        {
            'title': 'MetaMask Cüzdan Bağlama',
            'duration': '3:45',
            'thumbnail': '/static/help/thumbs/metamask.jpg',
            'video_url': '/help/videos/metamask.mp4',
            'description': 'NFT cüzdanınızı nasıl bağlarsınız',
            'level': 'Başlangıç'
        },
    ],
}

# ============================================================================
# CONTEXTUAL HELP (Sayfa içi yardım)
# ============================================================================

CONTEXTUAL_HELP = {
    'invoice_form': '''
        <div class="help-box">
            <h6><i class="bi-lightbulb text-warning"></i> Fatura Oluşturma İpuçları</h6>
            <ul class="mb-0">
                <li>Müşteri bulunamıyorsa "+" ile hızlıca ekleyin</li>
                <li>Ürün kodlarını yazarken otomatik tamamlama kullanın</li>
                <li>KDV oranı otomatik %20, değiştirebilirsiniz</li>
                <li>AI Asistan ile sesli fatura oluşturabilirsiniz</li>
            </ul>
        </div>
    ''',
    'dashboard': '''
        <div class="help-box">
            <h6><i class="bi-lightbulb text-warning"></i> Dashboard İpuçları</h6>
            <ul class="mb-0">
                <li>Widget'ları sürükle-bırak ile düzenleyin</li>
                <li>Filtreleri kullanarak dönem seçin</li>
                <li>Kartlara tıklayarak detay alın</li>
                <li>Dışa aktar ile rapor alın</li>
            </ul>
        </div>
    ''',
    'ai_assistant': '''
        <div class="help-box bg-info-subtle">
            <h6><i class="bi-robot text-primary"></i> AI Asistan Nasıl Kullanılır?</h6>
            <p class="mb-2"><strong>Sesli Komut:</strong></p>
            <ul>
                <li>Mikrofon ikonuna tıklayın</li>
                <li>Komutunuzu söyleyin: "Bu ay kaç fatura kestim?"</li>
                <li>AI yanıt verir ve gerekirse işlem yapar</li>
            </ul>
            <p class="mb-2 mt-3"><strong>Örnek Komutlar:</strong></p>
            <ul class="mb-0">
                <li>"Nakit durumum nedir?"</li>
                <li>"ABC firmasına 5000 TL fatura kes"</li>
                <li>"Bu ayki giderlerimi göster"</li>
            </ul>
        </div>
    ''',
}

# ============================================================================
# ONBOARDING CHECKLIST
# ============================================================================

ONBOARDING_CHECKLIST = {
    'new_user': [
        {'id': 'profile', 'title': 'Profil bilgilerini tamamla', 'completed': False},
        {'id': 'company', 'title': 'Şirket bilgilerini gir', 'completed': False},
        {'id': 'users', 'title': 'Kullanıcıları ekle (opsiyonel)', 'completed': False},
        {'id': 'first_invoice', 'title': 'İlk faturanı oluştur', 'completed': False},
        {'id': 'bank', 'title': 'Banka hesabı bağla (opsiyonel)', 'completed': False},
        {'id': 'ai_test', 'title': 'AI Asistan\'ı test et', 'completed': False},
        {'id': 'course', 'title': 'İlk eğitim kursunu tamamla', 'completed': False},
    ]
}

