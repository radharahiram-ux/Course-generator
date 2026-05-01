#!/usr/bin/env python3
"""
CrewAI Course Content Generator - CLI Entry Point

Generate educational content for CrewAI Campus using a crew of specialized agents.
Supports both direct Crew execution and Flow-based orchestration.

Usage:
    python -m src.main "Your Topic Here"
    python -m src.main "Building Custom Tools" --flow
    python -m src.main "Agent Memory Systems" --output lesson.md --flow
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from .crew import CourseGeneratorCrew
from .flow import CourseGeneratorFlow


# ASCII banner - clean and professional
BANNER = r"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║     ██████╗ ██████╗ ██╗   ██╗██████╗ ███████╗███████╗                        ║
║    ██╔════╝██╔═══██╗██║   ██║██╔══██╗██╔════╝██╔════╝                        ║
║    ██║     ██║   ██║██║   ██║██████╔╝███████╗█████╗                          ║
║    ██║     ██║   ██║██║   ██║██╔══██╗╚════██║██╔══╝                          ║
║    ╚██████╗╚██████╔╝╚██████╔╝██║  ██║███████║███████╗                        ║
║     ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝                        ║
║                                                                               ║
║     ██████╗ ███████╗███╗   ██╗███████╗██████╗  █████╗ ████████╗ ██████╗ ██████╗ ║
║    ██╔════╝ ██╔════╝████╗  ██║██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗║
║    ██║  ███╗█████╗  ██╔██╗ ██║█████╗  ██████╔╝███████║   ██║   ██║   ██║██████╔╝║
║    ██║   ██║██╔══╝  ██║╚██╗██║██╔══╝  ██╔══██╗██╔══██║   ██║   ██║   ██║██╔══██╗║
║    ╚██████╔╝███████╗██║ ╚████║███████╗██║  ██║██║  ██║   ██║   ╚██████╔╝██║  ██║║
║     ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝║
║                                                                               ║
║                    Powered by CrewAI 🚀                                       ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

CREW_INFO = """
🎓 Course Content Generator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your crew of expert agents:

  📐 Curriculum Architect  │ Plans structure and learning objectives
  ✍️  Content Writer        │ Creates lessons and code examples  
  🎯 Quiz Master           │ Designs assessments and exercises
  🔍 Code Reviewer         │ Ensures code quality and accuracy

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

FLOW_INFO = """
🔄 Flow Mode Enabled
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Using Flow + Crew hybrid orchestration:

  ✓ Topic Validation    │ Validates topic before generation
  ✓ Quality Routing     │ Re-runs if code review fails
  ✓ State Management    │ Tracks progress and metadata
  ✓ Error Handling      │ Graceful failure with reports

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate educational course content using CrewAI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Building Custom Tools in CrewAI"
  %(prog)s "Understanding Agent Memory" --flow
  %(prog)s "Multi-Agent Collaboration" --flow --difficulty advanced
  %(prog)s "Error Handling" --quiet --output error-handling.md
        """,
    )
    
    parser.add_argument(
        "topic",
        help="The topic to generate content for",
    )
    
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file path (default: output/<topic>-<timestamp>.md)",
    )
    
    parser.add_argument(
        "-f", "--flow",
        action="store_true",
        help="Use Flow-based orchestration (adds validation, quality routing, retries)",
    )
    
    parser.add_argument(
        "-d", "--difficulty",
        choices=["beginner", "intermediate", "advanced"],
        default="intermediate",
        help="Target difficulty level (default: intermediate)",
    )
    
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress verbose agent output",
    )
    
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Skip the ASCII banner",
    )
    
    parser.add_argument(
        "--max-retries",
        type=int,
        default=2,
        help="Max code review retry attempts in flow mode (default: 2)",
    )
    
    return parser.parse_args()


def generate_output_path(topic: str, use_flow: bool = False) -> Path:
    """Generate a default output path based on topic and timestamp."""
    # Sanitize topic for filename
    safe_topic = "".join(c if c.isalnum() or c in " -_" else "" for c in topic)
    safe_topic = safe_topic.replace(" ", "-").lower()[:50]
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    suffix = "-flow" if use_flow else ""
    
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    return output_dir / f"{safe_topic}{suffix}-{timestamp}.md"


def format_crew_output(topic: str, result: str, task_outputs: dict[str, str]) -> str:
    """Format the complete output document for Crew mode."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    document = f"""# Course Content: {topic}

> Generated by CrewAI Course Content Generator (Crew Mode)
> Date: {timestamp}

---

{result}

---

## Generation Details

This content was generated by a crew of 4 AI agents:
- **Curriculum Architect**: Planned the lesson structure
- **Content Writer**: Created the content and examples
- **Quiz Master**: Designed assessments
- **Code Reviewer**: Verified code quality

"""
    return document


def run_with_crew(args: argparse.Namespace, output_path: Path) -> int:
    """Run content generation using direct Crew execution."""
    print(CREW_INFO)
    print(f"📚 Topic: {args.topic}")
    print(f"📁 Output: {output_path}")
    print()
    
    try:
        print("🚀 Starting content generation...\n")
        print("=" * 80)
        
        crew = CourseGeneratorCrew(
            topic=args.topic,
            verbose=not args.quiet,
        )
        
        result = crew.run()
        task_outputs = crew.get_task_outputs()
        
        print("=" * 80)
        print("\n✅ Content generation complete!\n")
        
        # Format and save output
        formatted = format_crew_output(args.topic, result, task_outputs)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(formatted)
        
        print(f"📄 Saved to: {output_path}")
        print(f"📊 File size: {output_path.stat().st_size:,} bytes")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


def run_with_flow(args: argparse.Namespace, output_path: Path) -> int:
    """Run content generation using Flow-based orchestration."""
    print(FLOW_INFO)
    print(CREW_INFO)
    print(f"📚 Topic: {args.topic}")
    print(f"📊 Difficulty: {args.difficulty}")
    print(f"🔄 Max retries: {args.max_retries}")
    print(f"📁 Output: {output_path}")
    print()
    
    try:
        print("🚀 Starting Flow-based generation...\n")
        print("=" * 80)
        
        # Create and configure the flow
        flow = CourseGeneratorFlow()
        
        # Run the flow with inputs
        result = flow.kickoff(inputs={
            "topic": args.topic,
            "difficulty": args.difficulty,
        })
        
        print("=" * 80)
        
        # Get final content from state
        final_content = flow.state.final_content or str(result)
        
        # Add flow mode header
        header = f"""# Course Content: {args.topic}

> Generated by CrewAI Course Content Generator (Flow Mode)
> Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
> Difficulty: {args.difficulty}
> Review Attempts: {flow.state.review_attempts}
> Review Passed: {"✅ Yes" if flow.state.code_review_passed else "⚠️ Accepted with notes"}

---

"""
        
        formatted = header + final_content
        
        # Save output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(formatted)
        
        print(f"\n✅ Flow complete!")
        print(f"   Review attempts: {flow.state.review_attempts}")
        print(f"   Review passed: {flow.state.code_review_passed}")
        if flow.state.errors:
            print(f"   ⚠️ Notes: {len(flow.state.errors)} issue(s) logged")
        print()
        print(f"📄 Saved to: {output_path}")
        print(f"📊 File size: {output_path.stat().st_size:,} bytes")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Flow error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main() -> int:
    """Main entry point for the CLI."""
    args = parse_args()
    
    # Show banner
    if not args.no_banner:
        print(BANNER)
    
    # Determine output path
    output_path = args.output or generate_output_path(args.topic, args.flow)
    
    try:
        if args.flow:
            return run_with_flow(args, output_path)
        else:
            return run_with_crew(args, output_path)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation cancelled by user.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
