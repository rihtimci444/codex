from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Task:
    task_id: str
    files: List[str]
    depends_on: List[str]
    impact: float
    urgency: float
    effort: float
    risk: float


def task_priority_score(task: Task) -> float:
    """Higher is better. Balance impact/urgency against effort/risk."""
    return (task.impact * task.urgency) / max(0.1, (task.effort + task.risk))


def schedule_tasks(tasks: List[Task]) -> List[Task]:
    task_map: Dict[str, Task] = {task.task_id: task for task in tasks}
    indegree: Dict[str, int] = {task.task_id: 0 for task in tasks}
    graph: Dict[str, List[str]] = {task.task_id: [] for task in tasks}

    for task in tasks:
        for dep in task.depends_on:
            if dep in task_map:
                indegree[task.task_id] += 1
                graph[dep].append(task.task_id)

    ready = [task.task_id for task in tasks if indegree[task.task_id] == 0]
    ordered: List[Task] = []

    while ready:
        ready.sort(key=lambda task_id: task_priority_score(task_map[task_id]), reverse=True)
        task_id = ready.pop(0)
        ordered.append(task_map[task_id])

        for nxt in graph[task_id]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                ready.append(nxt)

    if len(ordered) != len(tasks):
        remaining = [task for task in tasks if task.task_id not in {item.task_id for item in ordered}]
        remaining.sort(key=task_priority_score, reverse=True)
        ordered.extend(remaining)

    return ordered
