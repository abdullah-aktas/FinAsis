# -*- coding: utf-8 -*-
try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover
    pygame = None

try:
    import ursina  # type: ignore
except Exception:  # pragma: no cover
    ursina = None
from typing import Dict, List, Optional, Tuple
import time
from dataclasses import dataclass
from enum import Enum
import uuid
from .accounting import AccountingSystem, Transaction, TransactionType
from datetime import datetime


class GameState(Enum):
    LOBBY = "lobby"
    IN_GAME = "in_game"
    END_GAME = "end_game"
    PAUSED = "paused"


@dataclass
class Player:
    id: str
    username: str
    level: int
    experience: int
    inventory: Dict
    cosmetics: List[str]
    subscription_tier: str
    stats: Dict


class GameEngine:
    def __init__(self, game_config: Dict):
        self.config = game_config
        self.players: Dict[str, Player] = {}
        self.game_state = GameState.LOBBY
        self.matchmaking_queue = []
        self.leaderboard = []
        self.season_data = {
            "current_season": 1,
            "start_time": time.time(),
            "end_time": time.time() + (30 * 24 * 60 * 60),  # 30 gün
            "rewards": {},
        }
        self.tournaments = []
        self.training_modules = {}
        self.community_content = []
        self.performance_metrics = {}
        self.accounting_system = AccountingSystem()
        self.inventory_challenges = {}
        self.tax_challenges = {}
        self.business_scenarios = {}
        self.learning_paths = {}

    def initialize_game(self):
        """Oyun başlangıç ayarlarını yapılandırır"""
        if pygame is None:
            raise RuntimeError("pygame not installed; GameEngine graphics disabled")
        pygame.init()
        self.setup_networking()
        self.load_assets()
        self.initialize_physics()
        self.initialize_cloud_save()
        self.initialize_performance_monitoring()
        self.load_training_modules()
        self.accounting_system.initialize_accounting_system()
        self.initialize_accounting_challenges()
        self.initialize_business_scenarios()
        self.initialize_learning_paths()

    def setup_networking(self):
        """Çok oyunculu özellikler için ağ altyapısını kurar"""
        # WebSocket bağlantısı
        # Matchmaking sistemi
        # Anti-cheat sistemi

    def load_assets(self):
        """Oyun varlıklarını yükler"""
        # Karakter modelleri
        # Haritalar
        # Ses efektleri
        # UI elementleri

    def initialize_physics(self):
        """Fizik motorunu başlatır"""
        # Collision detection
        # Movement physics
        # AR physics (TicaretinIzindeAR için)

    def start_matchmaking(self, player_id: str):
        """Oyuncuyu eşleşme kuyruğuna ekler"""
        if player_id not in self.matchmaking_queue:
            self.matchmaking_queue.append(player_id)
            self.try_match_players()

    def try_match_players(self):
        """Uygun oyuncuları eşleştirir"""
        if len(self.matchmaking_queue) >= 4:  # Minimum oyuncu sayısı
            matched_players = self.matchmaking_queue[:4]
            self.matchmaking_queue = self.matchmaking_queue[4:]
            self.start_game(matched_players)

    def start_game(self, player_ids: List[str]):
        """Yeni bir oyun oturumu başlatır"""
        self.game_state = GameState.IN_GAME
        # Oyun haritasını yükle
        # Oyuncuları spawn et
        # Oyun kurallarını başlat

    def update_player_stats(self, player_id: str, stats: Dict):
        """Oyuncu istatistiklerini günceller"""
        if player_id in self.players:
            self.players[player_id].stats.update(stats)
            self.update_leaderboard()

    def update_leaderboard(self):
        """Liderlik tablosunu günceller"""
        self.leaderboard = sorted(
            self.players.values(),
            key=lambda x: (
                x.stats.get("score", 0),
                x.stats.get("achievements", 0),
                x.stats.get("tournament_wins", 0),
            ),
            reverse=True,
        )

    def award_season_rewards(self):
        """Sezon sonu ödüllerini dağıtır"""
        for rank, player in enumerate(self.leaderboard[:10], 1):
            rewards = self.calculate_season_rewards(rank)
            self.distribute_rewards(player.id, rewards)

    def calculate_season_rewards(self, rank: int) -> Dict:
        """Sıralamaya göre ödülleri hesaplar"""
        return {
            "currency": 1000 * (11 - rank),
            "cosmetics": [f"season_{self.season_data['current_season']}_rank_{rank}"],
            "experience": 500 * (11 - rank),
        }

    def distribute_rewards(self, player_id: str, rewards: Dict):
        """Ödülleri oyuncuya dağıtır"""
        if player_id in self.players:
            player = self.players[player_id]
            player.inventory["currency"] += rewards["currency"]
            player.cosmetics.extend(rewards["cosmetics"])
            player.experience += rewards["experience"]

    def handle_subscription(self, player_id: str, tier: str):
        """Abonelik seviyesini günceller"""
        if player_id in self.players:
            self.players[player_id].subscription_tier = tier
            self.update_player_features(player_id)

    def update_player_features(self, player_id: str):
        """Oyuncunun abonelik seviyesine göre özellikleri günceller"""
        player = self.players[player_id]
        self.config["subscription_tiers"][player.subscription_tier]["features"]
        # Özellikleri aktifleştir/devre dışı bırak

    def initialize_cloud_save(self):
        """Bulut kayıt sistemini başlatır"""
        # Bulut kayıt bağlantısı
        # Otomatik kayıt ayarları
        # Çakışma çözümleme

    def initialize_performance_monitoring(self):
        """Performans izleme sistemini başlatır"""
        # FPS izleme
        # Bellek kullanımı izleme
        # Platform optimizasyonları

    def load_training_modules(self):
        """Eğitim modüllerini yükler"""
        # Temel eğitim modülleri
        self.training_modules = {
            "finance": {
                "title": "Finansal Okuryazarlık",
                "modules": [
                    "Temel Finansal Kavramlar",
                    "Bütçe Yönetimi",
                    "Yatırım Stratejileri",
                ],
            },
            "entrepreneurship": {
                "title": "Girişimcilik",
                "modules": ["İş Planı Hazırlama", "Pazar Analizi", "Risk Yönetimi"],
            },
            "accounting": {  # Muhasebe modülü eklendi
                "title": "Muhasebe",
                "modules": [
                    "Temel Muhasebe Kavramları",
                    "Muhasebe Kayıt İşlemleri",
                    "Finansal Tablolar",
                ],
            },
        }

    def start_tournament(self, tournament_config: Dict):
        """Turnuva başlatır"""
        rules = tournament_config.get("rules", {})
        max_participants = rules.get(
            "max_participants", tournament_config.get("max_participants", 64)
        )
        lock_on_start = rules.get("lock_on_start", True)
        min_level = rules.get("min_level", 0)
        now_ts = time.time()

        tournament = {
            "id": str(uuid.uuid4()),
            "name": tournament_config["name"],
            "type": tournament_config["type"],
            "start_time": now_ts,
            "end_time": now_ts + tournament_config["duration"],
            "participants": [],
            "prizes": tournament_config["prizes"],
            "rules": rules,
            # Genişletilmiş alanlar
            "status": "active",  # active, finished, canceled
            "max_participants": max_participants,
            "lock_on_start": lock_on_start,
            "min_level": min_level,
            "winners": [],
        }
        self.tournaments.append(tournament)

    def join_tournament(self, player_id: str, tournament_id: str) -> bool:
        """Oyuncuyu turnuvaya ekler"""
        ok, code = self.is_tournament_join_open(tournament_id, player_id)
        if not ok:
            return False
        t = self.get_tournament(tournament_id)
        assert t is not None
        if player_id not in t["participants"]:
            t["participants"].append(player_id)
        return True

    def is_tournament_join_open(
        self, tournament_id: str, player_id: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Katılım kurallarını kontrol eder.
        Dönüş: (ok: bool, code: str)
        code örnekleri: ok, not_found, inactive, player_not_found, time_window_closed,
        locked_after_start, capacity_full, below_min_level, already_joined
        """
        t = self.get_tournament(tournament_id)
        if t is None:
            return False, "not_found"
        if t.get("status") != "active":
            return False, "inactive"
        if player_id is not None and player_id not in self.players:
            return False, "player_not_found"
        now_ts = time.time()
        if not (t["start_time"] <= now_ts <= t["end_time"]):
            return False, "time_window_closed"
        if (
            t.get("lock_on_start", True)
            and now_ts > t["start_time"]
            and len(t["participants"]) > 0
        ):
            return False, "locked_after_start"
        if (
            t.get("max_participants")
            and len(t["participants"]) >= t["max_participants"]
        ):
            return False, "capacity_full"
        if player_id is not None:
            min_level = t.get("min_level", 0)
            if self.players[player_id].level < int(min_level):
                return False, "below_min_level"
            if player_id in t["participants"]:
                return False, "already_joined"
        return True, "ok"

    def join_tournament_ex(self, player_id: str, tournament_id: str) -> Dict:
        """Katılım denemesi için detaylı cevap döner: { ok: bool, code: str }"""
        ok, code = self.is_tournament_join_open(tournament_id, player_id)
        if ok:
            t = self.get_tournament(tournament_id)
            assert t is not None
            if player_id not in t["participants"]:
                t["participants"].append(player_id)
        return {"ok": ok, "code": code}

    def leave_tournament(self, player_id: str, tournament_id: str) -> bool:
        """Oyuncuyu turnuvadan çıkarır (başlamışsa kurallara göre engellenebilir)."""
        t = self.get_tournament(tournament_id)
        if t is None or t.get("status") != "active":
            return False
        if player_id in t["participants"]:
            # Başladıktan sonra ayrılma kuralı: varsayılan izin ver
            t["participants"].remove(player_id)
            return True
        return False

    def end_tournament(self, tournament_id: str, force: bool = False) -> bool:
        """
        Turnuvayı bitirir, sıralamayı oluşturur ve ödülleri dağıtır.
        Sıralama basitçe oyuncu skoruna göre yapılır (yüksekten düşüğe).
        """
        t = self.get_tournament(tournament_id)
        if t is None:
            return False
        now_ts = time.time()
        if not force and now_ts < t["end_time"]:
            return False
        if t.get("status") == "finished":
            return True
        # Sıralama (score'a göre)
        rankings = sorted(
            t["participants"],
            key=self._player_score_for_ranking,
            reverse=True,
        )
        t["winners"] = rankings[:3]
        # Ödüller
        self._award_tournament_prizes(t, rankings)
        # Kazanan istatistiklerini güncelle
        if rankings:
            winner_id = rankings[0]
            if winner_id in self.players:
                self.players[winner_id].stats["tournament_wins"] = (
                    self.players[winner_id].stats.get("tournament_wins", 0) + 1
                )
        t["status"] = "finished"
        return True

    def cancel_tournament(self, tournament_id: str) -> bool:
        """Turnuvayı iptal eder (ödül dağıtımı yapılmaz)."""
        t = self.get_tournament(tournament_id)
        if t is None:
            return False
        if t.get("status") == "finished":
            return False
        t["status"] = "canceled"
        return True

    def list_tournaments(self, status: Optional[str] = None):
        """Turnuvaları listeler (opsiyonel durum filtresi)."""
        if status is None:
            return list(self.tournaments)
        return [t for t in self.tournaments if t.get("status") == status]

    def my_tournaments(self, player_id: str):
        """Oyuncunun içinde olduğu turnuvalar."""
        return [t for t in self.tournaments if player_id in t.get("participants", [])]

    def get_tournament(self, tournament_id: str) -> Optional[Dict]:
        for t in self.tournaments:
            if t.get("id") == tournament_id:
                return t
        return None

    def _award_tournament_prizes(self, tournament: Dict, rankings: List[str]):
        """Prizleri dağıtır. tournament["prizes"] yapısı esnek desteklenir.
        Örn: {"1": {...}, "2": {...}, "3": {...}} veya list.
        """
        prizes = tournament.get("prizes", {})
        # Dict ise sıra anahtarları ile
        if isinstance(prizes, dict):
            for idx, pid in enumerate(rankings, start=1):
                prize = prizes.get(str(idx)) or prizes.get(idx)
                if not prize:
                    continue
                self._grant_reward(pid, prize)
        elif isinstance(prizes, list):
            for i, pid in enumerate(rankings):
                if i < len(prizes):
                    self._grant_reward(pid, prizes[i])
        else:
            # Tanınmayan tip: ilk 3'e sembolik ödül
            for i, pid in enumerate(rankings[:3]):
                self._grant_reward(
                    pid, {"currency": 1000 * (3 - i), "experience": 500 * (3 - i)}
                )

    def _grant_reward(self, player_id: str, reward: Dict):
        # distribute_rewards ile uyumlu alanlar: currency, cosmetics, experience
        safe_reward = {
            "currency": int(reward.get("currency", 0)),
            "cosmetics": list(reward.get("cosmetics", [])),
            "experience": int(reward.get("experience", 0)),
        }
        self.distribute_rewards(player_id, safe_reward)

    def _player_score_for_ranking(self, pid: str) -> int:
        p = self.players.get(pid)
        if not p or not isinstance(p.stats, dict):
            return 0
        return int(p.stats.get("score", 0))

    def record_tournament_score(
        self, tournament_id: str, player_id: str, score_delta: int
    ) -> bool:
        """Turnuva sürecinde oyuncunun skorunu artırır ve turnuva içi skor tablosunu tutar."""
        t = self.get_tournament(tournament_id)
        if not t or t.get("status") != "active":
            return False
        if player_id not in t.get("participants", []):
            return False
        if player_id not in self.players:
            return False
        # Global skor (lederboard) için
        p = self.players[player_id]
        if not isinstance(p.stats, dict):
            p.stats = {}
        p.stats["score"] = int(p.stats.get("score", 0)) + int(score_delta)
        # Turnuva içi skor
        if "scores" not in t:
            t["scores"] = {}
        t["scores"][player_id] = int(t["scores"].get(player_id, 0)) + int(score_delta)
        # Liderlik tablosunu genel olarak da güncelleyebiliriz
        self.update_leaderboard()
        return True

    def get_tournament_leaderboard(
        self, tournament_id: str, top_n: Optional[int] = None
    ) -> List[Dict]:
        """Turnuva özel skor tablosunu döndürür (oyuncu kimliği + skor)."""
        t = self.get_tournament(tournament_id)
        if not t:
            return []
        scores = t.get("scores", {})
        # Eğer skor tutulmadıysa global stat'ten üret
        if not scores:
            participants = t.get("participants", [])
            scores = {pid: self._player_score_for_ranking(pid) for pid in participants}
        ranking = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        if top_n is not None:
            ranking = ranking[:top_n]
        return [{"player_id": pid, "score": score} for pid, score in ranking]

    def tournament_public(self, tournament_id: str) -> Optional[Dict]:
        """Turnuvanın dış dünyaya sunulacak basit temsili."""
        t = self.get_tournament(tournament_id)
        if not t:
            return None
        return {
            "id": t["id"],
            "name": t["name"],
            "type": t["type"],
            "status": t.get("status"),
            "start_time": t["start_time"],
            "end_time": t["end_time"],
            "participants_count": len(t.get("participants", [])),
            "max_participants": t.get("max_participants"),
            "min_level": t.get("min_level"),
            "lock_on_start": t.get("lock_on_start", True),
            "winners": list(t.get("winners", [])),
        }

    def register_player(
        self, username: str, level: int = 1, experience: int = 0, currency: int = 0
    ) -> str:
        """Hızlı demo/test amaçlı basit oyuncu kaydı yapar ve player_id döner."""
        player_id = str(uuid.uuid4())
        self.players[player_id] = Player(
            id=player_id,
            username=username,
            level=level,
            experience=experience,
            inventory={"currency": currency},
            cosmetics=[],
            subscription_tier="free",
            stats={"score": 0, "achievements": 0, "tournament_wins": 0},
        )
        return player_id

    def submit_community_content(self, player_id: str, content: Dict) -> bool:
        """Topluluk içeriği gönderir"""
        if self._validate_community_content(content):
            content["id"] = str(uuid.uuid4())
            content["author_id"] = player_id
            content["submission_time"] = time.time()
            content["status"] = "pending"
            self.community_content.append(content)
            return True
        return False

    def _validate_community_content(self, content: Dict) -> bool:
        """Topluluk içeriğini doğrular"""
        # İçerik doğrulama kuralları
        # Uygunluk kontrolü
        # Telif hakkı kontrolü
        return True

    def optimize_performance(self):
        """Performans optimizasyonu yapar"""
        # Bellek optimizasyonu
        # Grafik optimizasyonu
        # Ağ optimizasyonu
        # Platform özel optimizasyonlar

    def get_player_stats(self, player_id: str) -> Dict:
        """Oyuncu istatistiklerini getirir"""
        if player_id in self.players:
            player = self.players[player_id]
            return {
                "score": player.stats.get("score", 0),
                "achievements": player.stats.get("achievements", 0),
                "tournament_wins": player.stats.get("tournament_wins", 0),
                "training_progress": player.stats.get("training_progress", {}),
                "community_contributions": player.stats.get(
                    "community_contributions", 0
                ),
            }
        return {}

    def save_game_state(self, player_id: str):
        """Oyun durumunu kaydeder"""
        if player_id in self.players:
            player = self.players[player_id]
            save_data = {
                "player_id": player_id,
                "stats": player.stats,
                "inventory": player.inventory,
                "progress": player.stats.get("progress", {}),
                "timestamp": time.time(),
            }
            # Bulut kayıt
            self._cloud_save(save_data)

    def _cloud_save(self, save_data: Dict):
        """Bulut kayıt işlemini gerçekleştirir"""
        # Bulut kayıt mantığı
        pass

    def process_game_transaction(
        self, player_id: str, transaction_type: str, amount: float
    ) -> bool:
        """Oyun içi işlemleri muhasebe sistemine kaydeder"""
        try:
            # Oyun içi işlemi muhasebe kaydına dönüştür
            transaction = Transaction(
                id=str(uuid.uuid4()),
                date=datetime.now(),
                type=TransactionType(transaction_type),
                description=f"Oyun içi {transaction_type} işlemi",
                debit_account="1001",  # Kasa hesabı
                credit_account="5001",  # Satış Gelirleri
                amount=amount,
                reference=f"GAME_{player_id}",
                status="completed",
            )

            # Muhasebe sistemine kaydet
            if self.accounting_system.record_transaction(transaction):
                # Oyun içi ödülleri ver
                self.add_player_experience(player_id, 10)

                # Görev ilerlemesini kontrol et
                self.check_accounting_challenges(player_id, transaction_type)
                return True
            return False
        except Exception as e:
            print(f"İşlem hatası: {str(e)}")
            return False

    def check_accounting_challenges(self, player_id: str, transaction_type: str):
        """Muhasebe görevlerinin ilerlemesini kontrol eder"""
        if player_id in self.players:
            self.players[player_id]

            # Envanter görevleri
            if transaction_type == "inventory":
                self.update_challenge_progress(player_id, "inventory_master")

            # Vergi görevleri
            elif transaction_type == "tax":
                self.update_challenge_progress(player_id, "tax_expert")

            # Finansal analiz görevleri
            elif transaction_type in ["sale", "purchase"]:
                self.update_challenge_progress(player_id, "financial_analyst")

    def update_challenge_progress(self, player_id: str, challenge_id: str):
        """Görev ilerlemesini günceller"""
        if player_id in self.players and challenge_id in self.inventory_challenges:
            player = self.players[player_id]
            challenge = self.inventory_challenges[challenge_id]

            # Görev ilerlemesini kaydet
            if "challenge_progress" not in player.stats:
                player.stats["challenge_progress"] = {}

            if challenge_id not in player.stats["challenge_progress"]:
                player.stats["challenge_progress"][challenge_id] = 0

            player.stats["challenge_progress"][challenge_id] += 1

            # Görev tamamlandı mı kontrol et
            if player.stats["challenge_progress"][challenge_id] >= len(
                challenge["tasks"]
            ):
                self.complete_challenge(player_id, challenge_id)

    def complete_challenge(self, player_id: str, challenge_id: str):
        """Görevi tamamlar ve ödül verir"""
        if player_id in self.players and challenge_id in self.inventory_challenges:
            player = self.players[player_id]
            challenge = self.inventory_challenges[challenge_id]

            # Ödülü ver
            player.experience += challenge["reward"]

            # Başarıyı kaydet
            if "completed_challenges" not in player.stats:
                player.stats["completed_challenges"] = []

            player.stats["completed_challenges"].append(challenge_id)

            # Yeni seviye kontrolü
            self.check_level_up(player_id)

    def get_player_accounting_progress(self, player_id: str) -> Dict:
        """Oyuncunun muhasebe öğrenme ilerlemesini döndürür"""
        if player_id in self.players:
            progress = self.accounting_system.get_learning_progress()

            # Görev ilerlemesini ekle
            player = self.players[player_id]
            if "challenge_progress" in player.stats:
                progress["challenges"] = player.stats["challenge_progress"]

            # Tamamlanan görevleri ekle
            if "completed_challenges" in player.stats:
                progress["completed_challenges"] = player.stats["completed_challenges"]

            return progress
        return {}

    def initialize_accounting_challenges(self):
        """Muhasebe görevlerini başlatır"""
        self.inventory_challenges = {
            "inventory_master": {
                "title": "Envanter Ustası",
                "description": "Envanter yönetimini öğren",
                "tasks": [
                    "İlk envanter kaydı oluştur",
                    "Stok güncellemesi yap",
                    "Envanter raporu oluştur",
                ],
                "reward": 500,
            },
            "tax_expert": {
                "title": "Vergi Uzmanı",
                "description": "Vergi hesaplamalarını öğren",
                "tasks": [
                    "KDV hesapla",
                    "Gelir vergisi hesapla",
                    "Vergi beyannamesi hazırla",
                ],
                "reward": 750,
            },
            "financial_analyst": {
                "title": "Finansal Analist",
                "description": "Finansal analiz yap",
                "tasks": [
                    "Finansal oranları hesapla",
                    "Bilanço analizi yap",
                    "Gelir tablosu analizi yap",
                ],
                "reward": 1000,
            },
        }

    def initialize_business_scenarios(self):
        """İş senaryolarını başlatır"""
        self.business_scenarios = {
            "startup": {
                "title": "Girişimci Yolculuğu",
                "description": "Kendi işletmenizi kurun ve yönetin",
                "stages": [
                    {
                        "title": "İş Planı Hazırlama",
                        "tasks": [
                            "Pazar araştırması yap",
                            "Finansal projeksiyon oluştur",
                            "Başlangıç maliyetlerini hesapla",
                        ],
                        "rewards": {"experience": 500, "currency": 1000},
                    },
                    {
                        "title": "İşletme Kurulumu",
                        "tasks": [
                            "Hesap planı oluştur",
                            "İlk muhasebe kayıtlarını yap",
                            "Vergi kaydı oluştur",
                        ],
                        "rewards": {"experience": 750, "currency": 1500},
                    },
                ],
            },
            "retail": {
                "title": "Perakende Mağaza Yönetimi",
                "description": "Bir perakende mağazasını yönetin",
                "stages": [
                    {
                        "title": "Envanter Yönetimi",
                        "tasks": [
                            "Stok takibi yap",
                            "Sipariş yönetimi",
                            "Envanter raporu oluştur",
                        ],
                        "rewards": {"experience": 600, "currency": 1200},
                    },
                    {
                        "title": "Finansal Yönetim",
                        "tasks": [
                            "Günlük kasa takibi",
                            "Maliyet analizi",
                            "Kâr marjı hesaplama",
                        ],
                        "rewards": {"experience": 800, "currency": 1600},
                    },
                ],
            },
        }

    def initialize_learning_paths(self):
        """Öğrenme yollarını başlatır"""
        self.learning_paths = {
            "beginner": {
                "title": "Muhasebe Temelleri",
                "description": "Muhasebenin temel kavramlarını öğrenin",
                "modules": ["temel_kavramlar", "kayit_islemleri"],
                "duration": "2 hafta",
                "difficulty": "Başlangıç",
            },
            "intermediate": {
                "title": "Finansal Analiz",
                "description": "Finansal tabloları analiz etmeyi öğrenin",
                "modules": ["finansal_tablo", "oran_analizi"],
                "duration": "3 hafta",
                "difficulty": "Orta",
            },
            "advanced": {
                "title": "İşletme Yönetimi",
                "description": "İşletme yönetimi ve stratejik kararlar",
                "modules": ["stratejik_planlama", "risk_yonetimi"],
                "duration": "4 hafta",
                "difficulty": "İleri",
            },
        }

    def start_business_scenario(self, player_id: str, scenario_id: str) -> bool:
        """İş senaryosunu başlatır"""
        if player_id in self.players and scenario_id in self.business_scenarios:
            player = self.players[player_id]
            self.business_scenarios[scenario_id]

            # Senaryo durumunu kaydet
            if "active_scenarios" not in player.stats:
                player.stats["active_scenarios"] = {}

            player.stats["active_scenarios"][scenario_id] = {
                "start_time": time.time(),
                "current_stage": 0,
                "completed_tasks": [],
            }

            return True
        return False

    def complete_scenario_task(
        self, player_id: str, scenario_id: str, task_index: int
    ) -> bool:
        """Senaryo görevini tamamlar"""
        if player_id in self.players and scenario_id in self.business_scenarios:
            player = self.players[player_id]
            scenario = self.business_scenarios[scenario_id]

            if scenario_id in player.stats["active_scenarios"]:
                scenario_state = player.stats["active_scenarios"][scenario_id]
                current_stage = scenario["stages"][scenario_state["current_stage"]]

                if task_index < len(current_stage["tasks"]):
                    # Görevi tamamla
                    if "completed_tasks" not in scenario_state:
                        scenario_state["completed_tasks"] = []

                    scenario_state["completed_tasks"].append(task_index)

                    # Ödülleri ver
                    player.experience += current_stage["rewards"]["experience"]
                    if "currency" in player.inventory:
                        player.inventory["currency"] += current_stage["rewards"][
                            "currency"
                        ]

                    # Tüm görevler tamamlandı mı kontrol et
                    if len(scenario_state["completed_tasks"]) == len(
                        current_stage["tasks"]
                    ):
                        self.complete_scenario_stage(player_id, scenario_id)

                    return True
        return False

    def complete_scenario_stage(self, player_id: str, scenario_id: str):
        """Senaryo aşamasını tamamlar"""
        if player_id in self.players and scenario_id in self.business_scenarios:
            player = self.players[player_id]
            scenario = self.business_scenarios[scenario_id]
            scenario_state = player.stats["active_scenarios"][scenario_id]

            # Sonraki aşamaya geç
            scenario_state["current_stage"] += 1

            # Tüm aşamalar tamamlandı mı kontrol et
            if scenario_state["current_stage"] >= len(scenario["stages"]):
                self.complete_business_scenario(player_id, scenario_id)

    def complete_business_scenario(self, player_id: str, scenario_id: str):
        """İş senaryosunu tamamlar"""
        if player_id in self.players and scenario_id in self.business_scenarios:
            player = self.players[player_id]

            # Senaryo tamamlama ödülü
            player.experience += 2000
            if "currency" in player.inventory:
                player.inventory["currency"] += 5000

            # Başarıyı kaydet
            if "completed_scenarios" not in player.stats:
                player.stats["completed_scenarios"] = []

            player.stats["completed_scenarios"].append(scenario_id)

            # Yeni seviye kontrolü
            self.check_level_up(player_id)

    # Duplicate method removed; single definition exists above

    def get_learning_path_progress(self, player_id: str) -> Dict:
        """Öğrenme yolu ilerlemesini döndürür"""
        if player_id in self.players:
            player = self.players[player_id]
            progress = {}

            for path_id, path in self.learning_paths.items():
                completed_modules = 0
                for module in path["modules"]:
                    if module in player.stats.get("completed_modules", []):
                        completed_modules += 1

                progress[path_id] = {
                    "title": path["title"],
                    "completed_modules": completed_modules,
                    "total_modules": len(path["modules"]),
                    "completion_percentage": (completed_modules / len(path["modules"]))
                    * 100,
                }

            return progress
        return {}

    def get_player_achievements(self, player_id: str) -> List[Dict]:
        """Oyuncunun başarılarını döndürür"""
        if player_id in self.players:
            player = self.players[player_id]
            achievements = []

            # Senaryo başarıları
            completed_scenarios = player.stats.get("completed_scenarios", [])
            if len(completed_scenarios) > 0:
                achievements.append(
                    {
                        "title": "İş Ustası",
                        "description": f"{len(completed_scenarios)} iş senaryosu tamamladınız",
                        "badge": "gold",
                    }
                )

            # Öğrenme başarıları
            completed_modules = player.stats.get("completed_modules", [])
            if len(completed_modules) > 0:
                achievements.append(
                    {
                        "title": "Öğrenme Yolcusu",
                        "description": f"{len(completed_modules)} modül tamamladınız",
                        "badge": "silver",
                    }
                )

            return achievements
        return []

    def add_player_experience(self, player_id: str, amount: int):
        """Oyuncuya deneyim puanı ekler"""
        if player_id in self.players:
            player = self.players[player_id]
            player.experience += amount
            self.check_level_up(player_id)

    def check_level_up(self, player_id: str):
        """Oyuncunun seviye atlayıp atlamadığını kontrol eder"""
        if player_id in self.players:
            player = self.players[player_id]
            required_exp = player.level * 1000  # Her seviye için 1000 deneyim puanı

            if player.experience >= required_exp:
                player.level += 1
                player.experience -= required_exp

                # Seviye atlama ödülü
                if "currency" in player.inventory:
                    player.inventory["currency"] += player.level * 500

                # Yeni özelliklerin kilidini aç
                self.unlock_level_features(player_id)

    def unlock_level_features(self, player_id: str):
        """Seviye atlamaya bağlı yeni özellikleri açar"""
        if player_id in self.players:
            player = self.players[player_id]

            # Yeni senaryolar
            if player.level >= 5 and "startup" not in player.stats.get(
                "unlocked_scenarios", []
            ):
                if "unlocked_scenarios" not in player.stats:
                    player.stats["unlocked_scenarios"] = []
                player.stats["unlocked_scenarios"].append("startup")

            # Yeni öğrenme yolları
            if player.level >= 10 and "intermediate" not in player.stats.get(
                "unlocked_paths", []
            ):
                if "unlocked_paths" not in player.stats:
                    player.stats["unlocked_paths"] = []
                player.stats["unlocked_paths"].append("intermediate")

            # İleri seviye özellikler
            if player.level >= 15 and "advanced" not in player.stats.get(
                "unlocked_paths", []
            ):
                player.stats["unlocked_paths"].append("advanced")

    def get_player_learning_progress(self, player_id: str) -> Dict:
        """Oyuncunun öğrenme ilerlemesini döndürür"""
        if player_id in self.players:
            player = self.players[player_id]
            progress = {
                "active_scenarios": player.stats.get("active_scenarios", {}),
                "completed_scenarios": player.stats.get("completed_scenarios", []),
                "learning_paths": self.get_learning_path_progress(player_id),
                "achievements": self.get_player_achievements(player_id),
                "unlocked_features": {
                    "scenarios": player.stats.get("unlocked_scenarios", []),
                    "paths": player.stats.get("unlocked_paths", []),
                },
            }
            return progress
        return {}
