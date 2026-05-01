"""
Flow-based orchestration for the Course Content Generator.

This module implements a Flow that orchestrates the content generation
process, adding pre-processing, post-processing, and conditional routing
capabilities on top of the core Crew.

The hybrid Flow + Crew pattern:
- Flow handles orchestration, state management, and routing
- Crew handles the actual content generation work
"""

from crewai.flow.flow import Flow, listen, start, router, or_
from pydantic import BaseModel
from typing import Literal
from datetime import datetime
import json

from .crew import CourseGeneratorCrew


class CourseFlowState(BaseModel):
    """
    State management for the course generation flow.
    
    Tracks the topic, generated content, quality metrics,
    and any errors encountered during generation.
    """
    # Input
    topic: str = ""
    difficulty: str = "intermediate"  # beginner, intermediate, advanced
    target_audience: str = "developers"
    
    # Processing state
    topic_validated: bool = False
    topic_analysis: str = ""
    
    # Generated content
    raw_content: str = ""
    curriculum_output: str = ""
    lesson_output: str = ""
    quiz_output: str = ""
    review_output: str = ""
    
    # Quality metrics
    code_review_passed: bool = False
    review_attempts: int = 0
    max_review_attempts: int = 2
    
    # Final output
    final_content: str = ""
    generation_metadata: dict = {}
    
    # Error handling
    errors: list[str] = []


class CourseGeneratorFlow(Flow[CourseFlowState]):
    """
    A Flow that orchestrates the course content generation process.
    
    This flow adds several capabilities on top of the raw Crew:
    
    1. **Topic Validation**: Ensures the topic is specific enough
    2. **Context Enrichment**: Adds metadata and context
    3. **Quality Routing**: Re-runs content if code review fails
    4. **Post-Processing**: Formats and packages final output
    
    Usage:
        flow = CourseGeneratorFlow()
        result = flow.kickoff(inputs={"topic": "Building Custom Tools"})
    """
    
    @start()
    def validate_topic(self) -> str:
        """
        Validate and analyze the input topic.
        
        Ensures the topic is:
        - Not empty
        - Specific enough to generate meaningful content
        - Related to CrewAI concepts
        """
        topic = self.state.topic
        
        if not topic or len(topic.strip()) < 3:
            self.state.errors.append("Topic is too short or empty")
            return "invalid"
        
        # Basic topic analysis (could be enhanced with LLM)
        topic_lower = topic.lower()
        
        # Check if it's CrewAI related
        crewai_keywords = [
            "agent", "crew", "task", "tool", "flow", "memory",
            "llm", "ai", "automation", "orchestration", "pipeline",
            "crewai", "delegation", "process"
        ]
        
        is_relevant = any(kw in topic_lower for kw in crewai_keywords)
        
        if not is_relevant:
            # Still allow it, but note it's not CrewAI-specific
            self.state.topic_analysis = (
                f"Topic '{topic}' doesn't appear to be CrewAI-specific. "
                "Content will be generated with a general AI/automation focus."
            )
        else:
            self.state.topic_analysis = (
                f"Topic '{topic}' is relevant to CrewAI concepts."
            )
        
        self.state.topic_validated = True
        return "valid"
    
    @listen("valid")
    def generate_content(self) -> str:
        """
        Run the main content generation Crew.
        
        This is where the heavy lifting happens - the Crew
        generates curriculum, content, quizzes, and reviews.
        """
        print(f"\n🚀 Starting content generation for: {self.state.topic}")
        print(f"   Analysis: {self.state.topic_analysis}")
        
        try:
            # Create and run the crew
            crew = CourseGeneratorCrew(
                topic=self.state.topic,
                verbose=True
            )
            
            result = crew.run()
            self.state.raw_content = result
            
            # Extract individual task outputs if available
            task_outputs = crew.get_task_outputs()
            if task_outputs:
                self.state.curriculum_output = task_outputs.get("curriculum", "")
                self.state.lesson_output = task_outputs.get("content", "")
                self.state.quiz_output = task_outputs.get("quiz", "")
                self.state.review_output = task_outputs.get("review", "")
            
            return "content_generated"
            
        except Exception as e:
            self.state.errors.append(f"Content generation failed: {str(e)}")
            return "generation_failed"
    
    @router(generate_content)
    def check_quality(self) -> Literal["quality_passed", "needs_revision", "max_retries"]:
        """
        Route based on code review results.
        
        If code review found significant issues and we haven't
        exceeded max retries, route back for revision.
        """
        self.state.review_attempts += 1
        
        # Check if review output indicates issues
        review_output = self.state.review_output.lower()
        
        # Look for indicators of problems
        problem_indicators = [
            "needs changes",
            "has issues",
            "incorrect",
            "won't run",
            "syntax error",
            "critical issue"
        ]
        
        has_problems = any(ind in review_output for ind in problem_indicators)
        
        # Look for indicators of approval
        approval_indicators = [
            "approved",
            "good",
            "correct",
            "production-ready",
            "no issues"
        ]
        
        is_approved = any(ind in review_output for ind in approval_indicators)
        
        if is_approved or not has_problems:
            self.state.code_review_passed = True
            return "quality_passed"
        elif self.state.review_attempts >= self.state.max_review_attempts:
            # Accept what we have after max attempts
            return "max_retries"
        else:
            return "needs_revision"
    
    @listen("needs_revision")
    def revise_content(self) -> str:
        """
        Re-run content generation with feedback from review.
        
        This creates a feedback loop where review comments
        inform the next generation attempt.
        """
        print(f"\n🔄 Revision attempt {self.state.review_attempts}")
        print(f"   Review feedback: {self.state.review_output[:200]}...")
        
        # Enhance topic with review feedback
        enhanced_topic = (
            f"{self.state.topic}\n\n"
            f"[REVISION NOTE: Previous code review found issues. "
            f"Please address: {self.state.review_output[:500]}]"
        )
        
        try:
            crew = CourseGeneratorCrew(
                topic=enhanced_topic,
                verbose=True
            )
            
            result = crew.run()
            self.state.raw_content = result
            
            task_outputs = crew.get_task_outputs()
            if task_outputs:
                self.state.review_output = task_outputs.get("review", "")
            
            return "content_generated"
            
        except Exception as e:
            self.state.errors.append(f"Revision failed: {str(e)}")
            return "generation_failed"
    
    @listen(or_("quality_passed", "max_retries"))
    def finalize_content(self) -> str:
        """
        Package the final content with metadata.
        
        Adds generation timestamp, review status, and
        any warnings or notes from the process.
        """
        # Build metadata
        self.state.generation_metadata = {
            "topic": self.state.topic,
            "difficulty": self.state.difficulty,
            "target_audience": self.state.target_audience,
            "generated_at": datetime.now().isoformat(),
            "review_attempts": self.state.review_attempts,
            "review_passed": self.state.code_review_passed,
            "topic_analysis": self.state.topic_analysis,
            "errors": self.state.errors if self.state.errors else None
        }
        
        # Build final content with header
        header = f"""---
# Course Content Generation Report
topic: "{self.state.topic}"
generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
review_status: {"✅ Passed" if self.state.code_review_passed else "⚠️ Accepted with notes"}
review_attempts: {self.state.review_attempts}
---

"""
        
        # Add any warnings
        if self.state.errors:
            header += "## ⚠️ Generation Notes\n\n"
            for error in self.state.errors:
                header += f"- {error}\n"
            header += "\n---\n\n"
        
        if not self.state.code_review_passed:
            header += (
                "## ⚠️ Review Note\n\n"
                "Content was accepted after maximum revision attempts. "
                "Please review code examples manually before use.\n\n"
                "---\n\n"
            )
        
        self.state.final_content = header + self.state.raw_content
        
        return "complete"
    
    @listen(or_("invalid", "generation_failed"))
    def handle_failure(self) -> str:
        """
        Handle generation failures gracefully.
        
        Creates an error report instead of crashing.
        """
        error_report = f"""---
# Course Generation Failed
topic: "{self.state.topic}"
timestamp: {datetime.now().isoformat()}
---

## Errors Encountered

"""
        for error in self.state.errors:
            error_report += f"- {error}\n"
        
        error_report += """

## Troubleshooting

1. Check that the topic is specific enough
2. Ensure API keys are configured
3. Try a more focused topic
4. Check the logs for detailed error messages
"""
        
        self.state.final_content = error_report
        return "complete"
    
    @listen("complete")
    def output_result(self) -> str:
        """
        Return the final content.
        
        This is the terminal node that returns the result.
        """
        print(f"\n✅ Generation complete!")
        print(f"   Review passed: {self.state.code_review_passed}")
        print(f"   Attempts: {self.state.review_attempts}")
        
        return self.state.final_content


def create_flow() -> CourseGeneratorFlow:
    """Factory function to create a configured flow."""
    return CourseGeneratorFlow()


def run_flow(topic: str, difficulty: str = "intermediate") -> str:
    """
    Convenience function to run the full flow.
    
    Args:
        topic: The lesson topic
        difficulty: beginner, intermediate, or advanced
        
    Returns:
        Generated course content
    """
    flow = create_flow()
    result = flow.kickoff(inputs={
        "topic": topic,
        "difficulty": difficulty
    })
    return result
