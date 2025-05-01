import numpy as np
from typing import Dict, List
import pandas as pd

class TradingEngine:
    def __init__(self):
        self.risk_levels = {
            TradeLevel.BEGINNER: 0.01,      # %1 risk
            TradeLevel.INTERMEDIATE: 0.02,   # %2 risk
            TradeLevel.ADVANCED: 0.03,       # %3 risk
            TradeLevel.EXPERT: 0.05,         # %5 risk
            TradeLevel.MASTER: 0.10          # %10 risk
        }
        
    def calculate_position_size(self, 
                              account_balance: float,
                              risk_level: TradeLevel,
                              stop_loss_pips: int) -> Dict:
        """Pozisyon büyüklüğü hesaplama"""
        max_risk = account_balance * self.risk_levels[risk_level]
        position_size = max_risk / (stop_loss_pips * 0.0001)
        
        return {
            "position_size": position_size,
            "max_risk_amount": max_risk,
            "potential_loss": max_risk,
            "required_margin": position_size * 0.01
        }
    
    def analyze_trading_style(self, trades: List[Dict]) -> Dict:
        """Ticaret stilini analiz et"""
        df = pd.DataFrame(trades)
        
        style = {
            "aggressive": 0,
            "conservative": 0,
            "scalper": 0,
            "swing_trader": 0
        }
        
        # Risk/ödül oranına göre stil belirleme
        avg_rr = df['profit'].mean() / abs(df['loss'].mean())
        if avg_rr > 2:
            style['conservative'] += 0.3
        else:
            style['aggressive'] += 0.3
            
        # İşlem süresine göre stil belirleme
        avg_duration = df['duration'].mean()
        if avg_duration < 60:  # 1 saatten az
            style['scalper'] += 0.5
        else:
            style['swing_trader'] += 0.5
            
        return style
