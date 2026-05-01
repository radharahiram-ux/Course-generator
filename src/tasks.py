"""
Task definitions for the Course Content Generator.

Tasks are executed in sequence to produce a complete lesson package:
1. Plan curriculum structure and objectives
2. Write lesson content with code examples
3. Create quiz questions and exercises
4. Review and polish all code examples
"""

from crewai import Task, Agent


def create_curriculum_task(agent: Agent, topic: str) -> Task:
    """
    Create the curriculum planning task.
    
    This task produces:
    - 3-5 clear learning objectives
    - Lesson structure with sections
    - Key concepts to cover
    - Prerequisites (if any)
    
    Args:
        agent: The curriculum architect agent
        topic: The lesson topic to plan
        
    Returns:
        Configured Task instance
    """
    return Task(
        description=f"""
        Design a comprehensive lesson plan for the topic: "{topic}"
        
        Your task:
        1. Analyze what learners need to know about this topic
        2. Define 3-5 specific, measurable learning objectives
        3. Create a logical lesson structure with clear sections
        4. Identify key concepts that must be explained
        5. Note any prerequisites learners should have
        
        Consider:
        - What does a developer need to DO with this knowledge?
        - What common mistakes should we help them avoid?
        - How does this topic connect to broader CrewAI concepts?
        
        Output a structured lesson plan that the content writer can follow.
        """,
        expected_output="""
        A detailed lesson plan containing:
        - Topic title
        - Target audience description
        - Prerequisites (if any)
        - 3-5 learning objectives (action-oriented, measurable)
        - Lesson outline with sections and key points
        - Suggested code examples to include
        - Common pitfalls to address
        """,
        agent=agent,
    )


def create_content_task(agent: Agent, topic: str) -> Task:
    """
    Create the content writing task.
    
    This task produces:
    - Full lesson content with explanations
    - Multiple code examples (introductory to advanced)
    - Tips and best practices
    - Clear transitions between sections
    
    Args:
        agent: The content writer agent
        topic: The lesson topic
        
    Returns:
        Configured Task instance
    """
    return Task(
        description=f"""
        Write comprehensive lesson content for: "{topic}"
        
        Using the curriculum plan provided, create:
        1. An engaging introduction that explains WHY this topic matters
        2. Clear explanations for each concept, building from simple to complex
        3. At least 3 practical code examples:
           - A simple "hello world" style example
           - A more realistic intermediate example
           - An advanced example showing best practices
        4. Tips, warnings, and best practices throughout
        5. A summary that reinforces key takeaways
        
        Writing guidelines:
        - Use a conversational but professional tone
        - Explain the "why" behind each concept, not just the "what"
        - Code examples should be complete and runnable
        - Include comments in code that explain important lines
        - Use analogies when helpful for complex concepts
        
        Format the content in Markdown with proper headings, code blocks, and emphasis.
        """,
        expected_output="""
        Complete lesson content in Markdown format including:
        - Title and introduction
        - Learning objectives (from curriculum plan)
        - Main content sections with explanations
        - At least 3 code examples with comments
        - Tips and best practices callouts
        - Summary of key points
        - "Next steps" or "Further reading" suggestions
        """,
        agent=agent,
    )


def create_quiz_task(agent: Agent, topic: str) -> Task:
    """
    Create the quiz and exercise task.
    
    This task produces:
    - 5 quiz questions of varying types
    - 1 hands-on coding exercise
    - Answer explanations
    
    Args:
        agent: The quiz master agent
        topic: The lesson topic
        
    Returns:
        Configured Task instance
    """
    return Task(
        description=f"""
        Create assessment materials for the lesson on: "{topic}"
        
        Design 5 quiz questions:
        1. At least one multiple choice question
        2. At least one true/false question  
        3. At least one "what's wrong with this code" question
        4. At least one conceptual question
        5. One question of your choice that tests practical understanding
        
        Design 1 hands-on exercise:
        - Should take 15-30 minutes to complete
        - Should apply multiple concepts from the lesson
        - Include clear instructions and acceptance criteria
        - Provide starter code if appropriate
        - Include hints (but don't give away the solution)
        
        For all questions:
        - Provide the correct answer
        - Explain WHY it's correct (or why others are wrong)
        - Reference which concept from the lesson it tests
        
        Questions should test understanding, not memorization!
        """,
        expected_output="""
        Assessment package containing:
        
        ## Quiz Questions (5 total)
        For each question:
        - Question text
        - Answer options (if applicable)
        - Correct answer
        - Explanation of why it's correct
        - Which learning objective it assesses
        
        ## Hands-on Exercise
        - Exercise title and description
        - Learning objectives practiced
        - Detailed instructions
        - Starter code (if applicable)
        - Acceptance criteria
        - Hints (progressive, 2-3 hints)
        - Solution outline (for instructor reference)
        """,
        agent=agent,
    )


def create_review_task(agent: Agent, topic: str) -> Task:
    """
    Create the code review task.
    
    This task:
    - Reviews all code examples for correctness
    - Checks for best practices
    - Suggests improvements
    - Ensures consistency
    
    Args:
        agent: The code reviewer agent
        topic: The lesson topic
        
    Returns:
        Configured Task instance
    """
    return Task(
        description=f"""
        Review all code examples from the lesson on: "{topic}"
        
        For each code example and exercise, verify:
        1. Code is syntactically correct and would run
        2. Code follows Python best practices (PEP 8, type hints where helpful)
        3. CrewAI library is used correctly and idiomatically
        4. Variable and function names are clear and descriptive
        5. Comments are helpful without being excessive
        6. Error handling is appropriate
        7. No security issues or bad patterns
        
        Also check:
        - Consistency in style across all examples
        - Progressive complexity (simple → advanced)
        - Whether examples actually demonstrate the concepts they claim to
        
        Provide:
        - A summary of code quality
        - Specific issues found (with line references if possible)
        - Suggested fixes for any problems
        - Final polished versions of code that needed changes
        
        If code is good, say so! Don't invent problems.
        """,
        expected_output="""
        Code review report containing:
        
        ## Overall Assessment
        - Summary of code quality (Good/Needs Work/Has Issues)
        - General observations
        
        ## Code Example Reviews
        For each example:
        - Example identifier/description
        - Status (Approved/Needs Changes)
        - Issues found (if any)
        - Suggested improvements
        - Corrected code (if changes needed)
        
        ## Final Recommendations
        - Any patterns to maintain
        - Suggestions for the content writer
        - Confidence level that code is production-ready
        """,
        agent=agent,
    )


def get_all_tasks(agents: dict[str, Agent], topic: str) -> list[Task]:
    """
    Create all tasks in execution order.
    
    Args:
        agents: Dictionary of agents by name
        topic: The lesson topic
        
    Returns:
        List of tasks in execution order
    """
    curriculum_task = create_curriculum_task(agents["curriculum_architect"], topic)
    content_task = create_content_task(agents["content_writer"], topic)
    quiz_task = create_quiz_task(agents["quiz_master"], topic)
    review_task = create_review_task(agents["code_reviewer"], topic)
    
    # Set up task dependencies via context
    content_task.context = [curriculum_task]
    quiz_task.context = [curriculum_task, content_task]
    review_task.context = [content_task, quiz_task]
    
    return [curriculum_task, content_task, quiz_task, review_task]
