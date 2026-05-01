"""
CrewAI Course Content Generator

A tool that generates educational content for CrewAI Campus
using a crew of specialized AI agents.

Supports two execution modes:
- **Crew Mode**: Direct sequential execution of agents
- **Flow Mode**: Flow-based orchestration with validation, routing, and retries
"""

from .agents import (
    create_curriculum_architect,
    create_content_writer,
    create_quiz_master,
    create_code_reviewer,
    get_all_agents,
)

from .tasks import (
    create_curriculum_task,
    create_content_task,
    create_quiz_task,
    create_review_task,
    get_all_tasks,
)

from .crew import (
    CourseGeneratorCrew,
    create_crew,
)

from .flow import (
    CourseGeneratorFlow,
    CourseFlowState,
    create_flow,
    run_flow,
)

__all__ = [
    # Agents
    "create_curriculum_architect",
    "create_content_writer",
    "create_quiz_master",
    "create_code_reviewer",
    "get_all_agents",
    # Tasks
    "create_curriculum_task",
    "create_content_task",
    "create_quiz_task",
    "create_review_task",
    "get_all_tasks",
    # Crew
    "CourseGeneratorCrew",
    "create_crew",
    # Flow
    "CourseGeneratorFlow",
    "CourseFlowState",
    "create_flow",
    "run_flow",
]

__version__ = "0.2.0"
