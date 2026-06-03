from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Task:
    id: str
    text: str
    label: int              # 1 = positive class (e.g. injection), 0 = negative
    attack_type: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Trajectory:
    task: Task
    skill_used: str
    reasoning: str
    prediction: int
    correct: bool


class TaskAdapter(ABC):
    @abstractmethod
    def train_tasks(self) -> list[Task]: ...

    @abstractmethod
    def selection_tasks(self) -> list[Task]: ...

    @abstractmethod
    def test_tasks(self) -> list[Task]: ...

    @abstractmethod
    def run(self, task: Task, skill: str) -> Trajectory: ...

    def score(self, trajectory: Trajectory) -> float:
        return 1.0 if trajectory.correct else 0.0

    def batch_score(self, trajectories: list[Trajectory]) -> float:
        if not trajectories:
            return 0.0
        return sum(self.score(t) for t in trajectories) / len(trajectories)
