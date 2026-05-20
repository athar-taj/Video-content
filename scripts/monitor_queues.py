import os
import sys
import asyncio
import time
import argparse
import logging
from sqlalchemy import select

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.repositories.manager import db_manager
from db.models.queue import WorkerStateModel
from ai.workflows.queue.queue_metrics import queue_metrics
from ai.workflows.queue.worker_registry import worker_registry

logging.basicConfig(level=logging.ERROR) # Suppress warnings

async def run_dashboard():
    """Prints a real-time terminal dashboard of the queue system."""
    # Prune offline workers first
    pruned_count = await worker_registry.prune_offline_workers(timeout_seconds=45)
    
    # 1. Fetch metrics
    metrics = await queue_metrics.get_full_dashboard_metrics()
    
    # 2. Fetch worker list
    async with db_manager.session_factory() as session:
        stmt = select(WorkerStateModel)
        result = await session.execute(stmt)
        workers = result.scalars().all()
        
    # Clear screen (cross-platform)
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("=" * 60)
    print("        🤖 ZEM JOB QUEUE & EXECUTION SYSTEM MONITOR 🤖        ")
    print("=" * 60)
    print(f"Time: {metrics['timestamp']['now']}")
    print("-" * 60)
    
    # Queue depths
    print("📥 QUEUE DEPTHS (REDIS):")
    for q_name, depth in metrics["queue_depths"].items():
        # Pad strings for alignment
        print(f"  • {q_name:<20} : {depth} pending jobs")
        
    print("-" * 60)
    
    # DB stats
    db_states = metrics["db_job_states"]
    print("📊 JOB STATUS STATS (DATABASE):")
    print(f"  • Total Jobs     : {db_states['total_jobs']}")
    print(f"  • Pending / Queued: {db_states['pending']} / {db_states['queued']}")
    print(f"  • Active Running : {db_states['active']}")
    print(f"  • Completed      : {db_states['completed']}")
    print(f"  • Failed / Dead  : {db_states['failed']} / {db_states['dead']}")
    print(f"  • Total Failures : {db_states['total_failures']}")
    
    print("-" * 60)
    
    # Worker states
    print(f"👷 ACTIVE WORKERS ({len(workers)}):")
    if not workers:
        print("  (No registered workers running)")
    else:
        for w in workers:
            active_jobs_str = ", ".join(w.active_jobs) if w.active_jobs else "None"
            print(f"  • Worker Name  : {w.worker_name}")
            print(f"    Queues       : {w.queue_name}")
            print(f"    Status       : {w.status.upper()}")
            print(f"    Active Jobs  : {active_jobs_str}")
            print(f"    Last Active  : {w.last_heartbeat.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
    print("=" * 60)
    if pruned_count > 0:
        print(f"ℹ️ Pruned {pruned_count} offline workers from registry.")
        print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Monitor RQ queues and worker states.")
    parser.add_argument("--watch", action="store_true", help="Continuously poll and display metrics.")
    parser.add_argument("--interval", type=int, default=2, help="Watch update interval in seconds.")
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    
    if args.watch:
        try:
            while True:
                loop.run_until_complete(run_dashboard())
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nExiting monitor...")
    else:
        loop.run_until_complete(run_dashboard())

if __name__ == "__main__":
    main()
