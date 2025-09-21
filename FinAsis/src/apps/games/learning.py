from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Lesson:
    title: str
    content: str
    duration: str
    difficulty: str
    video_url: str
    quiz: List[Dict]

@dataclass
class Exercise:
    title: str
    description: str
    scenario: str
    expected_output: str
    hints: List[str]

@dataclass
class LearningModule:
    id: str
    title: str
    lessons: List[Lesson] = field(default_factory=list)
    exercises: List[Exercise] = field(default_factory=list)
    completed_tasks: List[str] = field(default_factory=list)

@dataclass
class Achievement:
    id: str
    title: str
    description: str
    reward: int
    required_level: int

class LearningManager:
    def __init__(self):
        self.modules: Dict[str, LearningModule] = {}
        self.achievements: Dict[str, Achievement] = {}

    def add_module(self, module: LearningModule):
        self.modules[module.id] = module

    def complete_task(self, module_id: str, task_id: str):
        if module_id in self.modules:
            module = self.modules[module_id]
            if task_id not in module.completed_tasks:
                module.completed_tasks.append(task_id)

    def add_achievement(self, achievement: Achievement):
        self.achievements[achievement.id] = achievement

    def get_completed_tasks(self) -> List[str]:
        completed = []
        for module in self.modules.values():
            completed.extend(module.completed_tasks)
        return completed

    def get_achievements(self) -> List[Achievement]:
        return list(self.achievements.values()) 