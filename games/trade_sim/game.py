from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import photon
import json
from games.achievements import AchievementSystem
from games.quests import QuestSystem
from games.economy import EconomySystem
from games.social import SocialSystem
from games.notifications import NotificationSystem, NotificationType, NotificationPriority
import time
import datetime
from games.economy import Item, ItemRarity, CurrencyType
from games.quests import Quest, QuestType, QuestStatus
from ai_assistant.services.chat_service import ChatAIService
from blockchain.models import BlockchainTransaction, TokenTransaction, TokenContract

class TradeSim:
    def __init__(self):
        self.app = Ursina()
        
        # Photon ağ bağlantısı
        self.network = photon.PUN('your_app_id')
        
        # Oyun modu
        self.game_mode = 'classroom'  # classroom, freeplay
        
        # Oyun durumu
        self.game_state = {
            'players': {},
            'market_data': {},
            'teacher_controls': {},
            'teams': {},
            'guilds': {}
        }
        
        # Ortak sistemler
        self.achievement_system = AchievementSystem()
        self.quest_system = QuestSystem()
        self.economy_system = EconomySystem()
        self.social_system = SocialSystem()
        self.notification_system = NotificationSystem()
        
        # Sistemleri başlat
        self.achievement_system.initialize_achievements()
        self.quest_system.initialize_quests()
        self.economy_system.initialize_market()
        self._initialize_tradesim_content()
        # Oyun süresi takibi
        self.session_start_time = time.time()
        self.rest_notified = False
        self.rest_modal = None  # Modal pencere referansı
        self.rest_modal_active = False
        self.ai_service = ChatAIService()

    def _initialize_tradesim_content(self):
        # TradeSim'e özel başarımlar
        from games.achievements import AchievementType, AchievementTier, Achievement
        big_profit_achievement = Achievement(
            id="big_profit",
            name="Büyük Kar!",
            description="Bir ticarette 10.000 coin kar elde et.",
            type=AchievementType.TRADING,
            tier=AchievementTier.DIAMOND,
            progress=0,
            max_progress=1,
            rewards={"coins": 5000, "badge": "big_profit"},
            hidden=False,
            created_at=datetime.datetime.now()
        )
        self.achievement_system.achievements[big_profit_achievement.id] = big_profit_achievement
        # TradeSim'e özel görevler
        from games.quests import QuestType, QuestStatus, Quest
        tradesim_marathon_quest = Quest(
            id="tradesim_marathon",
            title="Ticaret Maratonu",
            description="Bir günde 100 ticaret yap.",
            type=QuestType.DAILY,
            requirements={"trades": 100},
            rewards={"coins": 2000, "badge": "marathoner"},
            start_time=datetime.datetime.now(),
            end_time=datetime.datetime.now() + datetime.timedelta(days=1),
            status=QuestStatus.ACTIVE,
            progress={"trades": 0}
        )
        self.quest_system.quests[tradesim_marathon_quest.id] = tradesim_marathon_quest
        # Ekonomi: Özel market ürünü
        from games.economy import Item, ItemRarity, CurrencyType
        special_item = Item(
            id="legendary_briefcase",
            name="Efsanevi Çanta",
            description="Tüm ticaretlerde %10 bonus kazanç sağlar.",
            rarity=ItemRarity.LEGENDARY,
            value={CurrencyType.COINS: 10000, CurrencyType.GEMS: 100, CurrencyType.TOKENS: 10},
            effects={"trade_bonus": 0.10}
        )
        self.economy_system.items[special_item.id] = special_item
        # Sosyal: Özel lonca
        self.social_system.create_clan("admin", "TradeSim Elitleri", "TSE", "En iyi traderların loncası.")

    def start_classroom(self, teacher_id):
        """Sınıf modunu başlat"""
        self.game_mode = 'classroom'
        self.game_state['teacher_controls'] = {
            'teacher_id': teacher_id,
            'paused': False,
            'scenario': None
        }
        
    def setup_world(self):
        """3D dünyayı hazırla"""
        # Temel dünya öğeleri
        ground = Entity(
            model='plane',
            scale=(100,1,100),
            texture='grass',
            collider='box'
        )
        
        # Ticaret merkezi
        trading_center = Entity(
            model='building',
            position=(0,0,0),
            scale=2
        )
        # --- Minecraft tarzı blok yerleştirme sistemi ---
        self.block_parent = Entity()
        self.block_size = 1
        self.blocks = {}
        self.selected_block_type = 'cube'  # Şimdilik sadece küp
        # Oyuncunun stand alanı (örnek: 10x1x10)
        self.stand_origin = (5, 1, 5)
        self.stand_size = (10, 1, 10)
        # Mouse ile blok ekle/kaldır
        def input(key, is_raw=False):
            if mouse.left:
                hit_info = mouse.hovered_entity
                if hit_info and hit_info in self.blocks.values():
                    if mouse.normal is not None:
                        pos = hit_info.position + mouse.normal * self.block_size
                        pos = tuple(round(x) for x in pos)
                        if self.is_in_stand_area(pos):
                            self.add_block(pos)
            if mouse.right:
                hit_info = mouse.hovered_entity
                if hit_info and hit_info in self.blocks.values():
                    pos = tuple(round(x) for x in hit_info.position)
                    self.remove_block(pos)
        # input fonksiyonunu global olarak bırakıyoruz, Ursina otomatik çağırır
        # Başlangıçta bir zemin bloğu ekle
        for x in range(self.stand_origin[0], self.stand_origin[0]+self.stand_size[0]):
            for z in range(self.stand_origin[2], self.stand_origin[2]+self.stand_size[2]):
                self.add_block((x, self.stand_origin[1], z))

    def is_in_stand_area(self, pos):
        x, y, z = pos
        ox, oy, oz = self.stand_origin
        sx, sy, sz = self.stand_size
        return (ox <= x < ox+sx) and (oy <= y < oy+sy+5) and (oz <= z < oz+sz)

    def add_block(self, pos):
        if pos in self.blocks:
            return
        block = Entity(
            parent=self.block_parent,
            model=self.selected_block_type,
            color=color.brown,
            position=pos,
            scale=self.block_size,
            collider='box'
        )
        self.blocks[pos] = block

    def remove_block(self, pos):
        if pos in self.blocks:
            destroy(self.blocks[pos])
            del self.blocks[pos]

    def on_trade(self, player_id, trade_data):
        # Ticaret işlemi sonrası çağrılır
        self.quest_system.update_quest_progress(player_id, "daily_trade_1", {"trades": 1})
        self.achievement_system.update_progress(player_id, "first_trade", 1)
        # Büyük kar başarımı
        if trade_data.get("profit", 0) >= 10000:
            self.achievement_system.update_progress(player_id, "big_profit", 1)
            self.notification_system.send_achievement_notification(player_id, "Büyük Kar!")
        rewards = self.economy_system.award_achievement_rewards(1)
        self.notification_system.send_achievement_notification(player_id, "İlk Ticaret")
        # ... diğer işlemler ...

    def on_friend_added(self, player_id, friend_id):
        self.social_system.add_friend(player_id, friend_id)
        self.notification_system.send_friend_notification(player_id, friend_id, "ekledi")

    def show_rest_modal(self):
        if self.rest_modal_active:
            return  # Zaten açık
        self.rest_modal_active = True
        self.rest_modal = WindowPanel(
            title='Sağlıklı Yaşam Molası',
            content=(
                Text("45 dakikadır oynuyorsun! Lütfen kısa bir mola ver ve su iç!", origin=(0,0)),
                Button('Kapat', scale=(0.4,0.1), on_click=self.close_rest_modal),
                Button('5 Dakika Mola Ver', scale=(0.4,0.1), on_click=self.take_rest)
            ),
            position=(0,0),
            popup=True,
            enabled=True,
            scale=(0.7,0.4)
        )
        self.rest_modal.z = 100  # Önde olsun

    def close_rest_modal(self):
        if self.rest_modal:
            destroy(self.rest_modal)
            self.rest_modal = None
        self.rest_modal_active = False

    def take_rest(self):
        self.session_start_time = time.time()  # Sayaç sıfırlanır
        self.rest_notified = False
        self.close_rest_modal()
        self.notification_system.send_notification(
            player_id="all",
            notification_type=NotificationType.SYSTEM,
            title="Mola Başladı!",
            message="Harika! 5 dakika mola veriyorsun. Sağlığın için teşekkürler!",
            priority=NotificationPriority.HIGH
        )

    def check_rest_reminder(self):
        # 45 dakika sonra dinlenme bildirimi gönder
        if not self.rest_notified and (time.time() - self.session_start_time) > 45*60:
            self.notification_system.send_notification(
                player_id="all",  # Tüm oyunculara veya aktif oyuncuya
                notification_type=NotificationType.SYSTEM,
                title="Sağlıklı Yaşam!",
                message="45 dakikadır oynuyorsun. Lütfen kısa bir mola ver ve su iç!",
                priority=NotificationPriority.HIGH
            )
            self.rest_notified = True
            self.show_rest_modal()  # Modal pencereyi göster

    def update(self):
        # Oyun döngüsünde çağrılır
        self.check_rest_reminder()
        # ... diğer güncellemeler ...

    def get_leaderboard(self, top_n=10):
        # Skora göre ilk N oyuncuyu getir
        players = list(self.game_state['players'].values())
        sorted_players = sorted(players, key=lambda p: p.get('score', 0), reverse=True)
        return sorted_players[:top_n]

    def show_leaderboard(self):
        leaderboard = self.get_leaderboard()
        print("--- Liderlik Tablosu ---")
        for idx, player in enumerate(leaderboard, 1):
            print(f"{idx}. {player['username']} - Puan: {player['score']}")

    def add_cosmetic_items(self):
        hat = Item(
            id="golden_hat",
            name="Altın Şapka",
            description="Sadece en iyi traderlar için.",
            rarity=ItemRarity.LEGENDARY,
            value={CurrencyType.COINS: 5000},
            effects={"style": "golden_hat"}
        )
        self.economy_system.items[hat.id] = hat
        # Yeni: Kozmetik eşyalar listesi
        self.cosmetic_items = {hat.id: hat}

    def equip_cosmetic(self, player_id, item_id):
        # Oyuncuya kozmetik eşya tak
        player = self.game_state['players'].get(player_id)
        if not player:
            return
        if 'cosmetics' not in player:
            player['cosmetics'] = []
        if item_id in self.cosmetic_items:
            if item_id not in player['cosmetics']:
                player['cosmetics'].append(item_id)
                self.notification_system.send_notification(
                    player_id=player_id,
                    notification_type=NotificationType.SYSTEM,
                    title="Kozmetik Eşya Takıldı!",
                    message=f"{self.cosmetic_items[item_id].name} karakterine takıldı.",
                    priority=NotificationPriority.LOW
                )

    def unequip_cosmetic(self, player_id, item_id):
        # Oyuncudan kozmetik eşya çıkar
        player = self.game_state['players'].get(player_id)
        if not player or 'cosmetics' not in player:
            return
        if item_id in player['cosmetics']:
            player['cosmetics'].remove(item_id)
            self.notification_system.send_notification(
                player_id=player_id,
                notification_type=NotificationType.SYSTEM,
                title="Kozmetik Eşya Çıkarıldı!",
                message=f"{self.cosmetic_items[item_id].name} karakterinden çıkarıldı.",
                priority=NotificationPriority.LOW
            )

    def start_weekly_tournament(self):
        self.notification_system.send_notification(
            player_id="all",
            notification_type=NotificationType.TOURNAMENT,
            title="Haftalık Turnuva Başladı!",
            message="En çok kar eden oyuncu büyük ödül kazanacak!",
            priority=NotificationPriority.HIGH
        )

    def on_quest_completed(self, player_id, quest_id):
        if quest_id == "tradesim_marathon":
            # Yeni bir zorluk aç
            new_quest = Quest(
                id="ultra_marathon",
                title="Ultra Maraton",
                description="Bir günde 500 ticaret yap.",
                type=QuestType.DAILY,
                requirements={"trades": 500},
                rewards={"coins": 10000, "badge": "ultra_marathoner"},
                start_time=datetime.datetime.now(),
                end_time=datetime.datetime.now() + datetime.timedelta(days=1),
                status=QuestStatus.ACTIVE,
                progress={"trades": 0}
            )
            self.quest_system.quests[new_quest.id] = new_quest
            self.notification_system.send_quest_notification(player_id, new_quest.title, False)

    def create_team(self, team_name, creator_id):
        if 'teams' not in self.game_state:
            self.game_state['teams'] = {}
        if team_name in self.game_state['teams']:
            return False  # Takım zaten var
        self.game_state['teams'][team_name] = {
            'members': [creator_id],
            'score': 0
        }
        self.notification_system.send_notification(
            player_id=creator_id,
            notification_type=NotificationType.SYSTEM,
            title="Takım Kuruldu!",
            message=f"{team_name} adında bir takım kurdun.",
            priority=NotificationPriority.LOW
        )
        return True

    def join_team(self, team_name, player_id):
        if 'teams' not in self.game_state or team_name not in self.game_state['teams']:
            return False
        team = self.game_state['teams'][team_name]
        if player_id not in team['members']:
            team['members'].append(player_id)
            self.notification_system.send_notification(
                player_id=player_id,
                notification_type=NotificationType.SYSTEM,
                title="Takıma Katıldın!",
                message=f"{team_name} takımına katıldın.",
                priority=NotificationPriority.LOW
            )
            return True
        return False

    def award_team(self, team_name, reward):
        if 'teams' not in self.game_state or team_name not in self.game_state['teams']:
            return False
        team = self.game_state['teams'][team_name]
        for member_id in team['members']:
            player = self.game_state['players'].get(member_id)
            if player:
                # reward bir dict ise, bakiyelere ekle
                if isinstance(reward, dict):
                    for k, v in reward.items():
                        if k in player:
                            player[k] += v
                        else:
                            player[k] = v
                else:
                    # Sadece puan ise skora ekle
                    player['score'] = player.get('score', 0) + reward
                self.notification_system.send_notification(
                    player_id=member_id,
                    notification_type=NotificationType.SYSTEM,
                    title="Takım Ödülü!",
                    message=f"Takım olarak ödül kazandınız: {reward}",
                    priority=NotificationPriority.HIGH
                )
        return True

    def start_battle_royale(self):
        self.game_state['battle_royale'] = {
            'active': True,
            'players': [],
            'eliminated': [],
            'start_time': time.time()
        }
        self.notification_system.send_notification(
            player_id="all",
            notification_type=NotificationType.SYSTEM,
            title="Battle Royale Başladı!",
            message="Hayatta kalan son oyuncu büyük ödül kazanacak!",
            priority=NotificationPriority.HIGH
        )

    def join_battle_royale(self, player_id):
        br = self.game_state.get('battle_royale')
        if not br or not br['active']:
            return False
        if player_id not in br['players']:
            br['players'].append(player_id)
            self.notification_system.send_notification(
                player_id=player_id,
                notification_type=NotificationType.SYSTEM,
                title="Battle Royale'e Katıldın!",
                message="Hayatta kal ve ödülü kazan!",
                priority=NotificationPriority.LOW
            )
            return True
        return False

    def eliminate_player_battle_royale(self, player_id):
        br = self.game_state.get('battle_royale')
        if not br or not br['active']:
            return False
        if player_id in br['players'] and player_id not in br['eliminated']:
            br['eliminated'].append(player_id)
            self.notification_system.send_notification(
                player_id=player_id,
                notification_type=NotificationType.SYSTEM,
                title="Elendin!",
                message="Battle Royale'den elendin.",
                priority=NotificationPriority.LOW
            )
            # Son oyuncu kaldıysa ödül ver
            if len(br['players']) - len(br['eliminated']) == 1:
                winner = [pid for pid in br['players'] if pid not in br['eliminated']][0]
                reward = self.economy_system.calculate_battle_royale_rewards(1, 0)
                player = self.game_state['players'].get(winner)
                if player:
                    for k, v in reward.items():
                        if k in player:
                            player[k] += v
                        else:
                            player[k] = v
                self.notification_system.send_notification(
                    player_id=winner,
                    notification_type=NotificationType.SYSTEM,
                    title="Battle Royale Şampiyonu!",
                    message=f"Tebrikler! Hayatta kalan son oyuncu oldun ve ödül kazandın: {reward}",
                    priority=NotificationPriority.HIGH
                )
                br['active'] = False
            return True
        return False

    def start_competitive_match(self, team1, team2):
        self.game_state['competitive_match'] = {
            'active': True,
            'teams': [team1, team2],
            'score': {team1: 0, team2: 0},
            'round': 1,
            'winner': None
        }
        self.notification_system.send_notification(
            player_id="all",
            notification_type=NotificationType.SYSTEM,
            title="Rekabetçi Maç Başladı!",
            message=f"{team1} vs {team2} arasında rekabetçi maç başladı!",
            priority=NotificationPriority.HIGH
        )

    def add_point_competitive(self, team):
        match = self.game_state.get('competitive_match')
        if not match or not match['active']:
            return False
        if team in match['score']:
            match['score'][team] += 1
            match['round'] += 1
            # 16'ya ulaşan kazanır (CS:GO kuralı)
            if match['score'][team] >= 16:
                match['winner'] = team
                match['active'] = False
                self.award_team(team, {'score': 500, 'coins': 1000})
                self.notification_system.send_notification(
                    player_id="all",
                    notification_type=NotificationType.SYSTEM,
                    title="Maç Sonucu!",
                    message=f"{team} takımı rekabetçi maçı kazandı!",
                    priority=NotificationPriority.HIGH
                )
            return True
        return False

    def join_competitive_match(self, team, player_id):
        match = self.game_state.get('competitive_match')
        if not match or not match['active']:
            return False
        if team in match['teams']:
            if 'members' not in match:
                match['members'] = {t: [] for t in match['teams']}
            if player_id not in match['members'][team]:
                match['members'][team].append(player_id)
                self.notification_system.send_notification(
                    player_id=player_id,
                    notification_type=NotificationType.SYSTEM,
                    title="Maça Katıldın!",
                    message=f"{team} takımında rekabetçi maça katıldın.",
                    priority=NotificationPriority.LOW
                )
                return True
        return False

    def create_guild(self, guild_name, creator_id):
        if 'guilds' not in self.game_state:
            self.game_state['guilds'] = {}
        if guild_name in self.game_state['guilds']:
            return False  # Lonca zaten var
        self.game_state['guilds'][guild_name] = {
            'members': [creator_id],
            'level': 1,
            'xp': 0
        }
        self.notification_system.send_notification(
            player_id=creator_id,
            notification_type=NotificationType.SYSTEM,
            title="Lonca Kuruldu!",
            message=f"{guild_name} adında bir lonca kurdun.",
            priority=NotificationPriority.LOW
        )
        return True

    def join_guild(self, guild_name, player_id):
        if 'guilds' not in self.game_state or guild_name not in self.game_state['guilds']:
            return False
        guild = self.game_state['guilds'][guild_name]
        if player_id not in guild['members']:
            guild['members'].append(player_id)
            self.notification_system.send_notification(
                player_id=player_id,
                notification_type=NotificationType.SYSTEM,
                title="Loncaya Katıldın!",
                message=f"{guild_name} loncasına katıldın.",
                priority=NotificationPriority.LOW
            )
            return True
        return False

    def award_guild(self, guild_name, reward):
        if 'guilds' not in self.game_state or guild_name not in self.game_state['guilds']:
            return False
        guild = self.game_state['guilds'][guild_name]
        for member_id in guild['members']:
            player = self.game_state['players'].get(member_id)
            if player:
                if isinstance(reward, dict):
                    for k, v in reward.items():
                        if k in player:
                            player[k] += v
                        else:
                            player[k] = v
                else:
                    player['score'] = player.get('score', 0) + reward
                self.notification_system.send_notification(
                    player_id=member_id,
                    notification_type=NotificationType.SYSTEM,
                    title="Lonca Ödülü!",
                    message=f"Lonca olarak ödül kazandınız: {reward}",
                    priority=NotificationPriority.HIGH
                )
        return True

    def initialize_needs(self, player_id):
        player = self.game_state['players'].get(player_id)
        if player:
            player['needs'] = {
                'energy': 100,
                'happiness': 100,
                'hunger': 100
            }

    def update_needs(self, player_id, delta_time):
        player = self.game_state['players'].get(player_id)
        if not player or 'needs' not in player:
            return
        needs = player['needs']
        needs['energy'] = max(0, needs['energy'] - 0.05 * delta_time)
        needs['happiness'] = max(0, needs['happiness'] - 0.03 * delta_time)
        needs['hunger'] = max(0, needs['hunger'] - 0.07 * delta_time)
        # Uyarı gönder
        if needs['energy'] < 20:
            self.notification_system.send_notification(
                player_id=player_id,
                notification_type=NotificationType.SYSTEM,
                title="Enerjin Azaldı!",
                message="Karakterinin enerjisi çok düşük. Dinlenmelisin!",
                priority=NotificationPriority.HIGH
            )
        if needs['happiness'] < 20:
            self.notification_system.send_notification(
                player_id=player_id,
                notification_type=NotificationType.SYSTEM,
                title="Mutluluğun Azaldı!",
                message="Karakterinin mutluluğu çok düşük. Eğlenmelisin!",
                priority=NotificationPriority.HIGH
            )
        if needs['hunger'] < 20:
            self.notification_system.send_notification(
                player_id=player_id,
                notification_type=NotificationType.SYSTEM,
                title="Açlık!",
                message="Karakterin çok aç. Yemek yemelisin!",
                priority=NotificationPriority.HIGH
            )

    def spawn_random_collectible(self):
        # Haritada rastgele bir konuma nadir nesne oluştur
        import random
        collectible_types = [
            {'id': 'rare_gem', 'name': 'Nadir Taş', 'reward': {'gems': 10}},
            {'id': 'mystic_box', 'name': 'Gizemli Kutu', 'reward': {'coins': 500}},
            {'id': 'legendary_card', 'name': 'Efsanevi Kart', 'reward': {'score': 1000}}
        ]
        collectible = random.choice(collectible_types)
        pos = (random.randint(0, 99), 1, random.randint(0, 99))
        if not hasattr(self, 'collectibles'):
            self.collectibles = []
        self.collectibles.append({
            'type': collectible,
            'position': pos,
            'collected': False
        })
        self.notification_system.send_notification(
            player_id="all",
            notification_type=NotificationType.SYSTEM,
            title="Haritada Yeni Nesne!",
            message=f"Haritada yeni bir {collectible['name']} belirdi! Bul ve topla!",
            priority=NotificationPriority.LOW
        )

    def collect_collectible(self, player_id, collectible_index):
        if not hasattr(self, 'collectibles'):
            return False
        if collectible_index < 0 or collectible_index >= len(self.collectibles):
            return False
        collectible = self.collectibles[collectible_index]
        if collectible['collected']:
            return False
        collectible['collected'] = True
        player = self.game_state['players'].get(player_id)
        if player:
            reward = collectible['type']['reward']
            for k, v in reward.items():
                if k in player:
                    player[k] += v
                else:
                    player[k] = v
            self.notification_system.send_notification(
                player_id=player_id,
                notification_type=NotificationType.SYSTEM,
                title="Nesne Toplandı!",
                message=f"{collectible['type']['name']} topladın ve ödül kazandın: {reward}",
                priority=NotificationPriority.HIGH
            )
            return True
        return False

    def get_ai_suggestion(self, player_id, context):
        # Oyuncuya AI ile öneri sun
        suggestion = self.ai_service.get_suggestion(context)
        self.notification_system.send_notification(
            player_id=player_id,
            notification_type=NotificationType.SYSTEM,
            title="AI Önerisi",
            message=suggestion,
            priority=NotificationPriority.LOW
        )
        return suggestion

    def ai_chat(self, player_id, message):
        # Oyuncu ile AI sohbeti
        response = self.ai_service.chat(message)
        self.notification_system.send_notification(
            player_id=player_id,
            notification_type=NotificationType.SYSTEM,
            title="AI Asistan",
            message=response,
            priority=NotificationPriority.LOW
        )
        return response

    def record_blockchain_transaction(self, player_id, title, tx_type, reference_id=None):
        # Basit bir blockchain işlemi kaydı (örnek)
        tx = BlockchainTransaction.objects.create(
            title=title,
            transaction_type=tx_type,
            reference_id=reference_id,
            notes=f"Oyuncu {player_id} işlemi",
        )
        self.notification_system.send_notification(
            player_id=player_id,
            notification_type=NotificationType.SYSTEM,
            title="Blockchain İşlemi",
            message=f"İşlemin blockchain'e kaydedildi: {title}",
            priority=NotificationPriority.LOW
        )
        return tx

    def award_nft_token(self, player_id, contract_id, amount=1):
        # Oyuncuya NFT veya token ödülü ver (örnek)
        contract = TokenContract.objects.get(id=contract_id)
        # TokenTransaction ile transfer kaydı
        TokenTransaction.objects.create(
            contract=contract,
            from_user=None,  # Sistemden
            to_user=player_id,
            amount=amount,
            transaction_type='mint',
            transaction_hash='auto-generated',
        )
        self.notification_system.send_notification(
            player_id=player_id,
            notification_type=NotificationType.SYSTEM,
            title="NFT/Token Ödülü!",
            message=f"{amount} adet NFT/token kazandın!",
            priority=NotificationPriority.HIGH
        )

if __name__ == '__main__':
    game = TradeSim()
    game.setup_world()
    game.app.run()
