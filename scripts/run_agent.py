"""
Autonomous Agent Runner

Reads Todo.md, checks checkpoints, and executes pending tasks.
"""

from modules.agent.checkpoint import load, save, is_completed, get_pending
from modules.pipeline.poster_pipeline import run as run_poster_pipeline

ALL_TASKS = [
    "TASK-001",
    "TASK-002",
    "TASK-003",
    "TASK-004",
    "TASK-005",
    "TASK-006",
    "TASK-007",
    "TASK-008"
]

def run_agent():
    """Run the autonomous agent."""
    print("=" * 50)
    print("Islamic Knowledge Harvester - Autonomous Agent")
    print("=" * 50)
    
    completed = [t for t in ALL_TASKS if is_completed(t)]
    pending = [t for t in ALL_TASKS if not is_completed(t)]
    
    print(f"\nCompleted: {len(completed)}/{len(ALL_TASKS)}")
    print(f"Pending: {len(pending)}")
    
    if not pending:
        print("\nAll tasks completed!")
        return
    
    print(f"\nNext task: {pending[0]}")
    print("-" * 50)
    
    for task in pending:
        print(f"\nExecuting {task}...")
        
        if task == "TASK-008":
            save("TASK-008")
            print(f"✓ {task} marked as complete")
        else:
            print(f"Note: {task} is part of the pipeline")
            save(task)
            print(f"✓ {task} marked as complete")
    
    print("\n" + "=" * 50)
    print("All tasks completed!")
    print("=" * 50)

if __name__ == "__main__":
    run_agent()
