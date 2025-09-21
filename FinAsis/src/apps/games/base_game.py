class BaseGame:
    """
    Tüm oyun sınıfları için temel yapı.
    Oyuncu bilgisi, oyun durumu ve temel işlemler burada tanımlanır.
    """

    def __init__(self, player=None):
        self.player = player or self._default_player()
        self.state = {
            'started': False,
            'paused': False,
            'completed': False,
            'last_saved': None
        }

    def _default_player(self):
        """Varsayılan oyuncu profili oluşturur"""
        return {
            'name': 'Oyuncu',
            'level': 1,
            'exp': 0,
            'inventory': {},
            'stats': {},
            'completed_quests': [],
        }

    def start(self):
        """Oyunu başlatır"""
        self.state['started'] = True
        self.state['paused'] = False
        print("[BaseGame] Oyun başlatıldı.")

    def pause(self):
        """Oyunu duraklatır"""
        if self.state['started']:
            self.state['paused'] = True
            print("[BaseGame] Oyun duraklatıldı.")

    def resume(self):
        """Duraklatılmış oyunu devam ettirir"""
        if self.state['paused']:
            self.state['paused'] = False
            print("[BaseGame] Oyun devam ettirildi.")

    def save(self, path='savegame.json'):
        """Oyun durumunu bir dosyaya kaydeder"""
        import json, datetime
        self.state['last_saved'] = datetime.datetime.now().isoformat()
        data = {'player': self.player, 'state': self.state}
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"[BaseGame] Oyun kaydedildi → {path}")

    def load(self, path='savegame.json'):
        """Oyun durumunu bir dosyadan yükler"""
        import json
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.player = data.get('player', self._default_player())
                self.state = data.get('state', self.state)
            print(f"[BaseGame] Oyun yüklendi ← {path}")
        except FileNotFoundError:
            print("[BaseGame] Kayıt dosyası bulunamadı, yeni oyun başlatılıyor.")
            self.player = self._default_player()

    def update(self):
        """Her oyun döngüsünde çalışacak güncelleme fonksiyonu"""
        pass

    def handle_event(self, event):
        """Oyun içi olayları işlemek için kullanılabilir"""
        print(f"[BaseGame] Olay: {event}")
