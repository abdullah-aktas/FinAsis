from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import time
import json
from enum import Enum

class EventType(Enum):
    GAME_START = "game_start"
    GAME_END = "game_end"
    TRADE = "trade"
    PURCHASE = "purchase"
    ACHIEVEMENT = "achievement"
    ERROR = "error"
    PERFORMANCE = "performance"

class PerformanceMetric(Enum):
    FPS = "fps"
    MEMORY = "memory"
    CPU = "cpu"
    NETWORK = "network"
    LOAD_TIME = "load_time"

@dataclass
class AnalyticsEvent:
    id: str
    type: EventType
    player_id: str
    timestamp: datetime
    data: Dict
    session_id: str

@dataclass
class PerformanceData:
    metric: PerformanceMetric
    value: float
    timestamp: datetime
    context: Dict

class AnalyticsSystem:
    def __init__(self):
        self.events: List[AnalyticsEvent] = []
        self.performance_data: List[PerformanceData] = []
        self.session_data: Dict[str, Dict] = {}
        self.error_logs: List[Dict] = []
        
    def track_event(self, event_type: EventType, player_id: str,
                   data: Dict, session_id: str) -> AnalyticsEvent:
        """Olay izleme"""
        event = AnalyticsEvent(
            id=str(uuid.uuid4()),
            type=event_type,
            player_id=player_id,
            timestamp=datetime.now(),
            data=data,
            session_id=session_id
        )
        
        self.events.append(event)
        return event
        
    def track_performance(self, metric: PerformanceMetric,
                         value: float, context: Dict = None) -> PerformanceData:
        """Performans metriklerini izle"""
        data = PerformanceData(
            metric=metric,
            value=value,
            timestamp=datetime.now(),
            context=context or {}
        )
        
        self.performance_data.append(data)
        return data
        
    def log_error(self, error_type: str, message: str,
                 stack_trace: str, context: Dict = None) -> Dict:
        """Hata kaydı"""
        error = {
            "id": str(uuid.uuid4()),
            "type": error_type,
            "message": message,
            "stack_trace": stack_trace,
            "timestamp": datetime.now(),
            "context": context or {}
        }
        
        self.error_logs.append(error)
        return error
        
    def start_session(self, player_id: str) -> str:
        """Yeni oturum başlat"""
        session_id = str(uuid.uuid4())
        self.session_data[session_id] = {
            "player_id": player_id,
            "start_time": datetime.now(),
            "end_time": None,
            "events": [],
            "performance_metrics": {}
        }
        return session_id
        
    def end_session(self, session_id: str):
        """Oturumu sonlandır"""
        if session_id in self.session_data:
            self.session_data[session_id]["end_time"] = datetime.now()
            
    def get_player_analytics(self, player_id: str,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> Dict:
        """Oyuncu analitiklerini getir"""
        player_events = [
            event for event in self.events
            if event.player_id == player_id
            and (not start_date or event.timestamp >= start_date)
            and (not end_date or event.timestamp <= end_date)
        ]
        
        return {
            "total_events": len(player_events),
            "event_types": self._count_event_types(player_events),
            "session_data": self._get_player_sessions(player_id),
            "performance_data": self._get_player_performance(player_id)
        }
        
    def _count_event_types(self, events: List[AnalyticsEvent]) -> Dict[str, int]:
        """Olay tiplerini say"""
        counts = {}
        for event in events:
            counts[event.type.value] = counts.get(event.type.value, 0) + 1
        return counts
        
    def _get_player_sessions(self, player_id: str) -> List[Dict]:
        """Oyuncu oturumlarını getir"""
        return [
            session for session in self.session_data.values()
            if session["player_id"] == player_id
        ]
        
    def _get_player_performance(self, player_id: str) -> Dict[str, List[float]]:
        """Oyuncu performans verilerini getir"""
        metrics = {}
        for data in self.performance_data:
            if data.context.get("player_id") == player_id:
                if data.metric.value not in metrics:
                    metrics[data.metric.value] = []
                metrics[data.metric.value].append(data.value)
        return metrics
        
    def export_analytics(self, format: str = "json") -> str:
        """Analitik verilerini dışa aktar"""
        data = {
            "events": [vars(event) for event in self.events],
            "performance_data": [vars(data) for data in self.performance_data],
            "error_logs": self.error_logs,
            "session_data": self.session_data
        }
        
        if format == "json":
            return json.dumps(data, default=str)
        else:
            raise ValueError(f"Desteklenmeyen format: {format}")
            
    def clear_old_data(self, days: int = 30):
        """Eski verileri temizle"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        self.events = [
            event for event in self.events
            if event.timestamp > cutoff_date
        ]
        
        self.performance_data = [
            data for data in self.performance_data
            if data.timestamp > cutoff_date
        ]
        
        self.error_logs = [
            error for error in self.error_logs
            if error["timestamp"] > cutoff_date
        ]
        
        self.session_data = {
            session_id: session
            for session_id, session in self.session_data.items()
            if session["start_time"] > cutoff_date
        } 