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
            }
        ],
        'quick_tips': [
            'Blockchain kayıtları silinemez ve değiştirilemez',
            'NFT\'lerinizi MetaMask cüzdanınıza alabilirsiniz',
            'Smart contract\'lar otomatik çalışır',
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
    ]
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

