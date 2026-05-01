"""
Crew definition for the Course Content Generator.

This module assembles the agents and tasks into a functional crew
that can generate complete lesson packages.
"""

from crewai import Crew, Process
from .agents import get_all_agents
from .tasks import get_all_tasks


class CourseGeneratorCrew:
    """
    A CrewAI crew that generates educational course content.
    
    The crew consists of four specialized agents working in sequence:
    1. Curriculum Architect - Plans the lesson structure
    2. Content Writer - Creates the actual content
    3. Quiz Master - Designs assessments
    4. Code Reviewer - Ensures code quality
    
    Usage:
        crew = CourseGeneratorCrew(topic="Building Custom Tools in CrewAI")
        result = crew.run()
    """
    
    def __init__(self, topic: str, verbose: bool = True):
        """
        Initialize the course generator crew.
        
        Args:
            topic: The topic to generate content for
            verbose: Whether to show detailed agent output
        """
        self.topic = topic
        self.verbose = verbose
        self._agents = None
        self._tasks = None
        self._crew = None
    
    @property
    def agents(self) -> dict:
        """Lazily create and return agents."""
        if self._agents is None:
            self._agents = get_all_agents()
        return self._agents
    
    @property
    def tasks(self) -> list:
        """Lazily create and return tasks."""
        if self._tasks is None:
            self._tasks = get_all_tasks(self.agents, self.topic)
        return self._tasks
    
    @property
    def crew(self) -> Crew:
        """Lazily create and return the crew."""
        if self._crew is None:
            self._crew = Crew(
                agents=list(self.agents.values()),
                tasks=self.tasks,
                process=Process.sequential,
                verbose=self.verbose,
            )
        return self._crew
    
    def run(self) -> str:
        """
        Execute the crew to generate course content.
        
        Returns:
            The complete lesson package as a string
        """
        result = self.crew.kickoff()
        return str(result)
    
    def get_task_outputs(self) -> dict[str, str]:
        """
        Get individual task outputs after running.
        
        Returns:
            Dictionary mapping task names to their outputs
        """
        task_names = ["curriculum", "content", "quiz", "review"]
        outputs = {}
        
        for name, task in zip(task_names, self.tasks):
            if task.output:
                outputs[name] = str(task.output)
        
        return outputs


def create_crew(topic: str, verbose: bool = True) -> CourseGeneratorCrew:
    """
    Factory function to create a course generator crew.
    
    Args:
        topic: The topic to generate content for
        verbose: Whether to show detailed output
        
    Returns:
        Configured CourseGeneratorCrew instance
    """
    return CourseGeneratorCrew(topic=topic, verbose=verbose)
