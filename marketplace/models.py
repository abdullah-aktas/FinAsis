from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class ContentCategory(enum.Enum):
    METAVERSE = "metaverse"
    AR = "augmented_reality"
    VR = "virtual_reality"
    MOBILE = "mobile"
    WEB = "web"
    ESPORTS = "esports"
    TOURNAMENT = "tournament"
    BATTLE_ROYALE = "battle_royale"
    GUILD = "guild"
    STORY_MODE = "story_mode"
    WELLNESS = "wellness"
    HEALTH_CHALLENGE = "health_challenge"
    MINDFULNESS = "mindfulness"

class TradeLevel(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"
    LEGEND = "legend"
    ELITE = "elite"
    GRANDMASTER = "grandmaster"

class AchievementType(enum.Enum):
    TRADE_MASTER = "trade_master"
    RISK_MANAGER = "risk_manager" 
    MARKET_GURU = "market_guru"
    TEAM_LEADER = "team_leader"
    MENTOR = "mentor"

class Content(Base):
    __tablename__ = 'contents'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author_id = Column(Integer)
    # NFT ve Blokzincir özellikleri
    nft_token_id = Column(String, unique=True)
    blockchain_verified = Column(Boolean, default=False)
    smart_contract_address = Column(String)
    
    # Gelişmiş içerik özellikleri
    content_type = Column(String)  # game, simulation, course, challenge
    difficulty_level = Column(Integer, default=1)
    skills_taught = Column(JSON)  # ["investing", "trading", "accounting"]
    completion_rewards = Column(JSON)  # {"fincoin": 100, "xp": 500}
    
    # Gamifikasyon
    leaderboard_enabled = Column(Boolean, default=True)
    achievements = Column(JSON)
    daily_challenges = Column(JSON)
    
    # Sosyal özellikler
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    
    # Ekonomik veriler
    price = Column(Float, default=0.0)
    fincoin_price = Column(Integer, default=0)
    creator_royalty = Column(Float, default=0.1)  # %10
    last_traded = Column(DateTime, default=datetime.utcnow)
    
    # Meta veriler
    downloads = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Metaverse ve XR özellikleri
    category = Column(Enum(ContentCategory))
    vr_compatible = Column(Boolean, default=False)
    ar_features = Column(JSON)  # {"markers": [], "3d_models": []}
    metaverse_location = Column(JSON)  # {"x": 0, "y": 0, "z": 0, "world": "finance_district"}
    
    # Yapay Zeka Entegrasyonu
    ai_difficulty_scaling = Column(Boolean, default=True)
    ai_teacher_enabled = Column(Boolean, default=False)
    ai_analytics = Column(JSON)  # {"learning_style": "", "success_rate": 0.0}
    
    # Gelişmiş Gamifikasyon
    seasonal_events = Column(JSON)
    trading_competitions = Column(JSON)
    team_challenges = Column(JSON)
    
    # İleri Seviye Oyunlaştırma
    trade_level = Column(Enum(TradeLevel), default=TradeLevel.BEGINNER)
    experience_points = Column(Integer, default=0)
    trader_rank = Column(Integer, default=0)
    badges = Column(JSON)  # {"golden_trader": true, "risk_master": false}
    trading_style = Column(JSON)  # {"aggressive": 0.8, "conservative": 0.2}
    
    # Yapay Zeka Eğitim Sistemi
    learning_path = Column(JSON)  # Kişiselleştirilmiş öğrenme yolu
    skill_tree = Column(JSON)  # Yetenek ağacı
    ai_mentor_logs = Column(JSON)  # AI mentör geri bildirimleri
    performance_metrics = Column(JSON)  # {"accuracy": 0.85, "risk_management": 0.9}
    
    # Sosyal Ticaret
    followers = Column(Integer, default=0)
    copy_traders = Column(Integer, default=0)
    trade_history = Column(JSON)  # Son işlemler
    trade_signals = Column(JSON)  # Paylaşılan sinyaller
    
    # Metaverse Özellikleri
    virtual_office = Column(JSON)  # {"location": [x,y,z], "design": "modern"}
    nft_trophies = Column(JSON)  # Kazanılan NFT ödüller
    avatar_items = Column(JSON)  # {"suits": [], "accessories": []}
    trade_room_access = Column(JSON)  # Özel ticaret odaları

    # E-Spor ve Turnuva Özellikleri
    tournament_stats = Column(JSON, default={
        "wins": 0,
        "losses": 0,
        "prize_money": 0,
        "rankings": [],
        "achievements": []
    })
    
    guild_info = Column(JSON, default={
        "guild_id": None,
        "role": None,
        "contributions": 0,
        "guild_achievements": []
    })
    
    battle_stats = Column(JSON, default={
        "battles_won": 0,
        "win_streak": 0,
        "best_strategy": None,
        "battle_rating": 1000
    })
    
    story_progress = Column(JSON, default={
        "chapter": 1,
        "completed_missions": [],
        "unlocked_characters": [],
        "story_achievements": []
    })
    
    trading_power = Column(Float, default=1.0)  # Çarpan etkisi
    mentor_bonus = Column(Float, default=0.0)   # Mentorlük bonusu
    trader_prestige = Column(Integer, default=0) # Prestij seviyesi

    # Sağlıklı Yaşam Özellikleri
    wellness_stats = Column(JSON, default={
        "daily_breaks_taken": 0,
        "exercise_minutes": 0,
        "water_intake": 0,
        "posture_score": 100,
        "eye_rest_breaks": 0,
        "mindfulness_minutes": 0
    })
    
    health_rewards = Column(JSON, default={
        "wellness_points": 0,
        "health_achievements": [],
        "streak_days": 0,
        "bonus_multiplier": 1.0
    })
    
    session_metrics = Column(JSON, default={
        "last_break_time": None,
        "total_session_time": 0,
        "break_notifications": True,
        "ergonomic_alerts": True
    })

    def calculate_trader_score(self):
        """Tüccar puanını hesapla"""
        score = 0
        if self.trade_history:
            win_rate = self.trade_history.get('win_rate', 0)
            profit_factor = self.trade_history.get('profit_factor', 1)
            risk_ratio = self.trade_history.get('risk_ratio', 0)
            
            score = (win_rate * 0.4 + profit_factor * 0.4 + risk_ratio * 0.2) * 100
        return min(score, 100)

    def update_trader_level(self):
        """Tüccar seviyesini güncelle"""
        score = self.calculate_trader_score()
        if score >= 90:
            self.trade_level = TradeLevel.MASTER
        elif score >= 80:
            self.trade_level = TradeLevel.EXPERT
        elif score >= 70:
            self.trade_level = TradeLevel.ADVANCED
        elif score >= 50:
            self.trade_level = TradeLevel.INTERMEDIATE
        else:
            self.trade_level = TradeLevel.BEGINNER

    def to_dict(self):
        base_dict = {
            "id": self.id,
            "title": self.title,
            "nft_info": {
                "token_id": self.nft_token_id,
                "verified": self.blockchain_verified,
                "contract": self.smart_contract_address
            },
            "content": {
                "type": self.content_type,
                "difficulty": self.difficulty_level,
                "skills": self.skills_taught,
                "rewards": self.completion_rewards
            },
            "social": {
                "likes": self.likes,
                "shares": self.shares,
                "comments": self.comments_count
            },
            "economics": {
                "price": self.price,
                "fincoin_price": self.fincoin_price,
                "royalty": self.creator_royalty,
                "last_traded": self.last_traded.isoformat()
            },
            "meta": {
                "downloads": self.downloads,
                "rating": self.rating,
                "created": self.created_at.isoformat(),
                "updated": self.updated_at.isoformat() if self.updated_at else None
            }
        }
        base_dict.update({
            "xr": {
                "category": self.category.value if self.category else None,
                "vr_compatible": self.vr_compatible,
                "ar_features": self.ar_features,
                "metaverse_location": self.metaverse_location
            },
            "ai": {
                "adaptive_difficulty": self.ai_difficulty_scaling,
                "ai_teacher": self.ai_teacher_enabled,
                "analytics": self.ai_analytics
            },
            "events": {
                "seasonal": self.seasonal_events,
                "competitions": self.trading_competitions,
                "team": self.team_challenges
            },
            "trading": {
                "level": self.trade_level.value,
                "xp": self.experience_points,
                "rank": self.trader_rank,
                "badges": self.badges,
                "style": self.trading_style,
                "score": self.calculate_trader_score()
            },
            "education": {
                "learning_path": self.learning_path,
                "skill_tree": self.skill_tree,
                "ai_mentor": self.ai_mentor_logs,
                "metrics": self.performance_metrics
            },
            "social_trading": {
                "followers": self.followers,
                "copy_traders": self.copy_traders,
                "history": self.trade_history,
                "signals": self.trade_signals
            },
            "metaverse": {
                "office": self.virtual_office,
                "trophies": self.nft_trophies,
                "avatar": self.avatar_items,
                "trade_rooms": self.trade_room_access
            },
            "esports": {
                "tournament_stats": self.tournament_stats,
                "guild_info": self.guild_info,
                "battle_stats": self.battle_stats,
                "story_progress": self.story_progress
            },
            "advanced_trading": {
                "trading_power": self.trading_power,
                "mentor_bonus": self.mentor_bonus,
                "trader_prestige": self.trader_prestige
            },
            "wellness": {
                "stats": self.wellness_stats,
                "rewards": self.health_rewards,
                "session": self.session_metrics
            }
        })
        return base_dict

    def check_break_needed(self) -> Dict:
        """Mola ihtiyacını kontrol et"""
        current_time = datetime.utcnow()
        last_break = self.session_metrics.get('last_break_time')
        
        if last_break:
            last_break = datetime.fromisoformat(last_break)
            minutes_passed = (current_time - last_break).total_seconds() / 60
            
            if minutes_passed >= 45:
                return {
                    "need_break": True,
                    "message": "45 dakika oldu! Kısa bir mola verelim mi?",
                    "health_tips": [
                        "🚶‍♂️ 5 dakika yürüyüş yapın",
                        "👀 20-20-20 kuralı: 20 dakikada bir, 20 saniye boyunca 20 feet uzağa bakın",
                        "💧 Su için ve gözlerinizi dinlendirin",
                        "🧘‍♂️ Kısa bir nefes egzersizi yapın"
                    ],
                    "reward": {
                        "wellness_points": 50,
                        "bonus": "Sağlıklı Tüccar Rozeti"
                    }
                }
        return {"need_break": False}

    def update_wellness_stats(self, activity_type: str, value: float):
        """Sağlık istatistiklerini güncelle"""
        if activity_type in self.wellness_stats:
            self.wellness_stats[activity_type] += value
            
            # Sağlık başarıları kontrolü
            if activity_type == "daily_breaks_taken" and self.wellness_stats[activity_type] >= 5:
                self.health_rewards["health_achievements"].append("Dinlenme Ustası")
            elif activity_type == "exercise_minutes" and self.wellness_stats[activity_type] >= 30:
                self.health_rewards["health_achievements"].append("Aktif Tüccar")
