from transformers import AutoModelForCausalLM, AutoTokenizer
import numpy as np
from typing import Dict, List

class AITeacher:
    def __init__(self):
        self.model_name = "finasis/finance-gpt"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
        
    def analyze_learning_style(self, user_interactions: List[Dict]) -> str:
        """Öğrencinin öğrenme stilini analiz et"""
        styles = {
            "visual": 0,
            "auditory": 0,
            "kinesthetic": 0
        }
        
        for interaction in user_interactions:
            if interaction["type"] in ["3d_simulation", "ar_game"]:
                styles["kinesthetic"] += 1
            elif interaction["type"] in ["video", "chart"]:
                styles["visual"] += 1
            elif interaction["type"] in ["audio", "voice_chat"]:
                styles["auditory"] += 1
                
        return max(styles.items(), key=lambda x: x[1])[0]
    
    def generate_personalized_lesson(self, 
                                   topic: str,
                                   difficulty: int,
                                   learning_style: str) -> Dict:
        """Kişiselleştirilmiş ders içeriği oluştur"""
        prompt = f"Create a {learning_style} learning experience for {topic} at difficulty level {difficulty}"
        
        # AI model ile içerik oluştur
        response = self.model.generate(
            self.tokenizer.encode(prompt, return_tensors="pt"),
            max_length=1000,
            temperature=0.7
        )
        
        content = self.tokenizer.decode(response[0])
        
        return {
            "topic": topic,
            "content": content,
            "style": learning_style,
            "difficulty": difficulty,
            "interactive_elements": self._generate_interactive_elements(learning_style)
        }
    
    def _generate_interactive_elements(self, style: str) -> List[Dict]:
        """Öğrenme stiline göre interaktif elementler oluştur"""
        elements = []
        if style == "visual":
            elements.extend([
                {"type": "3d_chart", "data": "stock_market_visualization"},
                {"type": "ar_overlay", "data": "financial_indicators"}
            ])
        elif style == "kinesthetic":
            elements.extend([
                {"type": "trading_simulation", "difficulty": "adaptive"},
                {"type": "vr_market", "mode": "practice"}
            ])
        return elements
