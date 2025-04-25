from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import os
import uuid

@dataclass
class BetaFeature:
    id: str
    name: str
    description: str
    status: str  # "active", "testing", "completed"
    feedback_count: int
    average_rating: float
    issues: List[Dict]

@dataclass
class UserFeedback:
    id: str
    user_id: str
    feature_id: str
    rating: int
    comment: str
    timestamp: datetime
    status: str  # "new", "reviewed", "resolved"

class BetaManager:
    def __init__(self):
        self.features: Dict[str, BetaFeature] = {}
        self.feedback: Dict[str, UserFeedback] = {}
        self.beta_testers: List[str] = []
        self.feedback_file = "beta_feedback.json"
        
    def initialize_beta_features(self):
        """Beta özelliklerini başlatır"""
        beta_features = [
            {
                "id": "cloud_save",
                "name": "Bulut Kayıt",
                "description": "Oyun durumunu bulutta saklama",
                "status": "testing",
                "feedback_count": 0,
                "average_rating": 0.0,
                "issues": []
            },
            {
                "id": "performance_opt",
                "name": "Performans Optimizasyonu",
                "description": "Oyun performansı iyileştirmeleri",
                "status": "testing",
                "feedback_count": 0,
                "average_rating": 0.0,
                "issues": []
            },
            {
                "id": "cross_platform",
                "name": "Çoklu Platform Desteği",
                "description": "Farklı platformlarda oyun deneyimi",
                "status": "testing",
                "feedback_count": 0,
                "average_rating": 0.0,
                "issues": []
            }
        ]
        
        for feature in beta_features:
            self.features[feature["id"]] = BetaFeature(**feature)
            
    def add_beta_tester(self, user_id: str) -> bool:
        """Beta testçisi ekler"""
        if user_id not in self.beta_testers:
            self.beta_testers.append(user_id)
            return True
        return False
        
    def submit_feedback(self, user_id: str, feature_id: str,
                       rating: int, comment: str) -> Optional[UserFeedback]:
        """Kullanıcı geri bildirimi gönderir"""
        if feature_id not in self.features:
            return None
            
        feedback = UserFeedback(
            id=str(uuid.uuid4()),
            user_id=user_id,
            feature_id=feature_id,
            rating=rating,
            comment=comment,
            timestamp=datetime.now(),
            status="new"
        )
        
        self.feedback[feedback.id] = feedback
        self._update_feature_stats(feature_id, rating)
        self._save_feedback()
        
        return feedback
        
    def _update_feature_stats(self, feature_id: str, rating: int):
        """Özellik istatistiklerini günceller"""
        feature = self.features[feature_id]
        total_rating = feature.average_rating * feature.feedback_count
        feature.feedback_count += 1
        feature.average_rating = (total_rating + rating) / feature.feedback_count
        
    def report_issue(self, user_id: str, feature_id: str,
                    title: str, description: str) -> bool:
        """Hata raporu gönderir"""
        if feature_id not in self.features:
            return False
            
        issue = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": title,
            "description": description,
            "timestamp": datetime.now(),
            "status": "open"
        }
        
        self.features[feature_id].issues.append(issue)
        return True
        
    def get_feature_feedback(self, feature_id: str,
                           status: Optional[str] = None) -> List[UserFeedback]:
        """Özellik geri bildirimlerini getirir"""
        feedback_list = [
            f for f in self.feedback.values()
            if f.feature_id == feature_id
        ]
        
        if status:
            feedback_list = [f for f in feedback_list if f.status == status]
            
        return sorted(feedback_list, key=lambda x: x.timestamp, reverse=True)
        
    def update_feedback_status(self, feedback_id: str, status: str) -> bool:
        """Geri bildirim durumunu günceller"""
        if feedback_id in self.feedback:
            self.feedback[feedback_id].status = status
            self._save_feedback()
            return True
        return False
        
    def _save_feedback(self):
        """Geri bildirimleri kaydeder"""
        feedback_data = {
            "features": {f.id: vars(f) for f in self.features.values()},
            "feedback": {f.id: vars(f) for f in self.feedback.values()},
            "beta_testers": self.beta_testers
        }
        
        with open(self.feedback_file, 'w') as f:
            json.dump(feedback_data, f, default=str)
            
    def load_feedback(self):
        """Geri bildirimleri yükler"""
        if os.path.exists(self.feedback_file):
            with open(self.feedback_file, 'r') as f:
                data = json.load(f)
                
            self.features = {
                f["id"]: BetaFeature(**f)
                for f in data["features"].values()
            }
            
            self.feedback = {
                f["id"]: UserFeedback(**f)
                for f in data["feedback"].values()
            }
            
            self.beta_testers = data["beta_testers"]
            
    def get_feature_status(self, feature_id: str) -> Optional[str]:
        """Özellik durumunu getirir"""
        if feature_id in self.features:
            return self.features[feature_id].status
        return None
        
    def promote_feature(self, feature_id: str) -> bool:
        """Özelliği tam sürüme yükseltir"""
        if feature_id in self.features:
            feature = self.features[feature_id]
            if feature.status == "testing" and feature.average_rating >= 4.0:
                feature.status = "completed"
                return True
        return False 