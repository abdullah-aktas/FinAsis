from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any

from django.contrib.auth.models import AnonymousUser

from ..models import PlayerProfile


@dataclass
class GameSettings:
    difficulty: str
    hints: bool
    params: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "difficulty": self.difficulty,
            "hints": self.hints,
            "params": self.params,
        }


def _calc_success_rate(pp: PlayerProfile, category: str | None = None) -> float:
    stats = pp.stats or {}
    if category:
        c = stats.get(category, {"correct": 0, "total": 0})
        if c.get("total", 0) == 0:
            return 0.5
        return c.get("correct", 0) / max(1, c.get("total", 0))
    # overall
    total = 0
    correct = 0
    for c in stats.values():
        total += c.get("total", 0)
        correct += c.get("correct", 0)
    return (correct / total) if total else 0.5


def recommend_settings(user, game: str) -> GameSettings:
    # Guest user default settings
    if isinstance(user, AnonymousUser) or not user.is_authenticated:
        return GameSettings(
            difficulty="medium",
            hints=True,
            params={
                "question_count": 10,
                "volatility": 1.0,
                "scenario_level": "standard",
            },
        )

    pp = getattr(user, "player_profile", None)  # type: ignore[assignment]
    if not pp:
        pp = PlayerProfile.objects.create(user=user)

    # Decide category mapping for the game
    game_category_map = {
        "quiz": "Eğitim",
        "stock-market": "Yatırım",
        "budget-challenge": "Bütçe",
        "investment-simulator": "Yatırım",
        "trade-sim": "Ticaret",
    }
    category = game_category_map.get(game, "Eğitim")
    sr = _calc_success_rate(pp, category=category)

    # Adaptive difficulty based on success rate
    difficulty = pp.difficulty
    if pp.difficulty == "adaptive":
        if sr >= 0.8:
            difficulty = "hard"
        elif sr <= 0.4:
            difficulty = "easy"
        else:
            difficulty = "medium"

    # Hints on for lower success rates
    hints = sr < 0.7

    # Game-specific params
    params: Dict[str, Any] = {}
    if game == "quiz":
        params = {
            "question_count": 10,
            "difficulty_mix": {
                "easy": 0.6 if difficulty == "easy" else 0.2,
                "medium": 0.6 if difficulty == "medium" else 0.3,
                "hard": 0.6 if difficulty == "hard" else 0.2,
            },
        }
    elif game == "stock-market":
        params = {
            "volatility": {"easy": 0.8, "medium": 1.0, "hard": 1.3}.get(difficulty, 1.0),
            "starting_cash": {"easy": 150000, "medium": 100000, "hard": 70000}.get(difficulty, 100000),
        }
    elif game == "budget-challenge":
        params = {
            "scenario_level": {"easy": "beginner", "medium": "standard", "hard": "advanced"}.get(difficulty, "standard"),
        }
    elif game == "investment-simulator":
        params = {
            "market_noise": {"easy": 0.8, "medium": 1.0, "hard": 1.2}.get(difficulty, 1.0),
        }
    elif game == "trade-sim":
        params = {
            "demand_variance": {"easy": 0.8, "medium": 1.0, "hard": 1.25}.get(difficulty, 1.0),
            "starting_capital": {"easy": 12000, "medium": 10000, "hard": 8000}.get(difficulty, 10000),
        }

    # Save last recommended
    pp.last_recommended = {"game": game, "difficulty": difficulty, "hints": hints, "params": params}
    pp.save(update_fields=["last_recommended"])

    return GameSettings(difficulty=difficulty, hints=hints, params=params)


def track_event(user, game: str, category: str, correct: bool) -> Dict[str, Any]:
    if isinstance(user, AnonymousUser) or not user.is_authenticated:
        return {"tracked": False, "reason": "anonymous"}

    pp = getattr(user, "player_profile", None)  # type: ignore[assignment]
    if not pp:
        pp = PlayerProfile.objects.create(user=user)

    pp.record_event(category=category, correct=correct)

    return {
        "tracked": True,
        "stats": pp.stats,
        "skills": {
            "trade": pp.skill_trade,
            "invest": pp.skill_invest,
            "budget": pp.skill_budget,
            "education": pp.skill_education,
        },
    }
