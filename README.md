# 🎓 Course Generator Flow

**A production-ready example of CrewAI's Flow + Crew hybrid pattern** — demonstrating how to combine orchestration logic with multi-agent collaboration.

Give it a topic, get a complete lesson package: curriculum, content, quizzes, and reviewed code examples.

[![CrewAI](https://img.shields.io/badge/Built%20with-CrewAI-coral)](https://crewai.com)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎯 What This Demonstrates

This project showcases the **Flow + Crew hybrid pattern** — the recommended architecture for production CrewAI applications:

- **Flow** handles orchestration: validation, routing, retries, state management
- **Crew** handles execution: multi-agent collaboration on complex tasks

```
┌─────────────────────────────────────────────────────────────┐
│                         FLOW LAYER                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │ Validate │ →  │  Route   │ →  │ Finalize │              │
│  └──────────┘    └────┬─────┘    └──────────┘              │
│                       │                 ↑                   │
│                       ▼                 │                   │
│              ┌────────────────┐         │                   │
│              │   CREW LAYER   │─────────┘                   │
│              │                │                             │
│              │  ┌──────────┐  │                             │
│              │  │ Architect│  │                             │
│              │  └────┬─────┘  │                             │
│              │       ↓        │                             │
│              │  ┌──────────┐  │                             │
│              │  │  Writer  │  │                             │
│              │  └────┬─────┘  │                             │
│              │       ↓        │                             │
│              │  ┌──────────┐  │                             │
│              │  │Quiz Master│ │                             │
│              │  └────┬─────┘  │                             │
│              │       ↓        │                             │
│              │  ┌──────────┐  │                             │
│              │  │ Reviewer │  │                             │
│              │  └──────────┘  │                             │
│              └────────────────┘                             │
└─────────────────────────────────────────────────────────────┘
```

### Why This Pattern?

| Challenge | Flow Solves It | Crew Solves It |
|-----------|---------------|----------------|
| Input validation | ✅ Pre-flight checks | |
| Complex multi-step work | | ✅ Agent collaboration |
| Quality control loops | ✅ Conditional routing | |
| Error recovery | ✅ Graceful fallbacks | |
| State persistence | ✅ Typed state management | |
| Specialized expertise | | ✅ Role-based agents |

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/crewAIInc/course-generator-flow.git
cd course-generator-flow

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install dependencies
pip install -e .

# Set your API key
export OPENAI_API_KEY="your-key-here"
```

### Generate Your First Course

```bash
# Basic generation (Crew mode)
python -m src.main "Building Custom Tools in CrewAI"

# With Flow orchestration (recommended)
python -m src.main "Building Custom Tools in CrewAI" --flow

# Advanced options
python -m src.main "Agent Memory Systems" --flow --difficulty advanced --output lesson.md
```

---

## 🏗️ Architecture

### The Crew (4 Specialized Agents)

| Agent | Role | Responsibility |
|-------|------|----------------|
| 📐 **Curriculum Architect** | Instructional Designer | Plans structure, defines learning objectives |
| ✍️ **Content Writer** | Technical Writer | Creates lessons, explanations, code examples |
| 🎯 **Quiz Master** | Assessment Specialist | Designs questions and hands-on exercises |
| 🔍 **Code Reviewer** | Senior Engineer | Ensures code quality and correctness |

### The Flow (Orchestration Layer)

```python
class CourseGeneratorFlow(Flow[CourseFlowState]):
    
    @start()
    def validate_topic(self):
        """Pre-flight validation before spending tokens."""
        
    @listen("valid")
    def generate_content(self):
        """Run the Crew to generate content."""
        
    @router(generate_content)
    def check_quality(self):
        """Route based on code review results."""
        
    @listen("needs_revision")
    def revise_content(self):
        """Re-run with review feedback."""
        
    @listen(or_("quality_passed", "max_retries"))
    def finalize_content(self):
        """Package output with metadata."""
```

### State Management

```python
class CourseFlowState(BaseModel):
    # Input
    topic: str = ""
    difficulty: str = "intermediate"
    
    # Processing
    topic_validated: bool = False
    review_attempts: int = 0
    code_review_passed: bool = False
    
    # Output
    final_content: str = ""
    errors: list[str] = []
```

---

## 📖 Usage

### Command Line

```bash
# Simple (Crew mode - direct execution)
python -m src.main "Your Topic Here"

# Flow mode (recommended for production)
python -m src.main "Your Topic Here" --flow

# All options
python -m src.main "Topic" \
    --flow \                    # Use Flow orchestration
    --difficulty advanced \     # beginner/intermediate/advanced
    --output lesson.md \        # Custom output path
    --max-retries 3 \          # Quality retry attempts
    --quiet                     # Less verbose output
```

### Programmatic

```python
# Crew mode (simple)
from src import CourseGeneratorCrew

crew = CourseGeneratorCrew(topic="Building Custom Tools")
result = crew.run()

# Flow mode (production)
from src import CourseGeneratorFlow

flow = CourseGeneratorFlow()
result = flow.kickoff(inputs={
    "topic": "Building Custom Tools",
    "difficulty": "intermediate"
})

# Access state after completion
print(f"Review passed: {flow.state.code_review_passed}")
print(f"Attempts: {flow.state.review_attempts}")
```

---

## 📁 Project Structure

```
course-generator-flow/
├── README.md
├── pyproject.toml
├── src/
│   ├── __init__.py         # Package exports
│   ├── agents.py           # Agent definitions (roles, goals, backstories)
│   ├── tasks.py            # Task definitions (descriptions, expected outputs)
│   ├── crew.py             # Crew assembly (agents + tasks + process)
│   ├── flow.py             # Flow orchestration (validation, routing, state)
│   └── main.py             # CLI entry point
├── output/                 # Generated content
└── examples/               # Sample outputs
```

---

## 🎨 Output Example

Generated content includes:

```markdown
# Course Content: Building Custom Tools in CrewAI

> Generated by CrewAI Course Generator (Flow Mode)
> Review Passed: ✅ Yes
> Attempts: 1

---

## Learning Objectives
1. Understand when and why to create custom tools
2. Implement a basic custom tool using the @tool decorator
3. Build tools that interact with external APIs
...

## Introduction
Tools are what give your agents superpowers...

## Code Examples

### Example 1: Simple Calculator Tool
```python
from crewai.tools import tool

@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression."""
    return str(eval(expression))
```

...

## Quiz Questions
1. What decorator is used to create a custom tool?
   - [ ] @agent
   - [x] @tool
   - [ ] @task
...
```

---

## 🔧 Customization

### Using Different Models

```python
# In src/agents.py
from crewai import Agent, LLM

llm = LLM(model="gpt-4o")  # or claude-3-5-sonnet, etc.

return Agent(
    role="Curriculum Architect",
    llm=llm,
    # ...
)
```

### Adding New Agents

```python
# In src/agents.py
def create_visual_designer() -> Agent:
    return Agent(
        role="Visual Designer",
        goal="Create diagrams and visual aids for lessons",
        backstory="You are a technical illustrator who...",
    )
```

### Extending the Flow

```python
# In src/flow.py
@listen("finalize_content")
def generate_visuals(self):
    """Add a visual generation step."""
    # Use the visual designer agent
    pass
```

---

## 💡 Example Topics

**Beginner:**
- "Introduction to CrewAI Agents"
- "Your First Crew: Hello World"
- "Understanding Tasks and Goals"

**Intermediate:**
- "Building Custom Tools in CrewAI"
- "Agent Memory and Context"
- "Multi-Agent Collaboration Patterns"

**Advanced:**
- "Flow-Based Orchestration Patterns"
- "Production Deployment Strategies"
- "Advanced Task Delegation"

---

## 🤝 Contributing

Contributions welcome! Areas of interest:

- [ ] Additional agent types (e.g., Visual Designer, Translator)
- [ ] More output formats (HTML, PDF, SCORM)
- [ ] Integration with LMS platforms
- [ ] Caching for faster regeneration
- [ ] Parallel task execution where possible

---

## 📄 License

MIT License - Use freely in your own projects.

---

## 🔗 Resources

- [CrewAI Documentation](https://docs.crewai.com)
- [CrewAI Flows Guide](https://docs.crewai.com/concepts/flows)
- [CrewAI GitHub](https://github.com/crewAIInc/crewAI)
- [CrewAI Discord](https://discord.gg/crewai)

---

<p align="center">
  <strong>Built with ❤️ using <a href="https://crewai.com">CrewAI</a></strong>
</p>
