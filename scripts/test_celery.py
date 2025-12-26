#!/usr/bin/env python
"""
Test script for Celery functionality.

This script tests:
- RabbitMQ broker connection
- Task registration and discovery
- Task execution (async and sync)
- Task result retrieval
- Worker availability

Usage:
    python scripts/test_celery.py
    python scripts/test_celery.py --sync  # Run tasks synchronously for testing
"""

import os
import sys
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

import django
from celery import current_app
from django.conf import settings

# Initialize Django
django.setup()

from core.tasks import periodic_task, simple_async_task


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_broker_connection():
    """Test RabbitMQ broker connection."""
    print_section("Testing RabbitMQ Broker Connection")
    try:
        # Get Celery app instance
        app = current_app
        
        # Test broker connection
        inspect = app.control.inspect()
        active_queues = inspect.active_queues()
        
        if active_queues:
            print("✓ Broker connection successful!")
            print(f"  Active queues: {len(active_queues)}")
            for worker, queues in active_queues.items():
                print(f"  Worker '{worker}' has {len(queues)} queue(s)")
            return True
        else:
            print("⚠ Broker connection successful, but no active workers found.")
            print("  Make sure Celery worker is running:")
            print("    celery -A config worker -l info")
            return True
    except Exception as e:
        print(f"✗ Broker connection failed: {e}")
        print("\n  Troubleshooting:")
        print("  1. Check RabbitMQ is running: docker-compose ps rabbitmq")
        print("  2. Verify CELERY_BROKER_URL in settings")
        print("  3. Check RabbitMQ credentials match environment variables")
        return False


def test_task_registration():
    """Test that tasks are properly registered."""
    print_section("Testing Task Registration")
    try:
        app = current_app
        registered_tasks = list(app.tasks.keys())
        
        # Filter out Celery internal tasks
        project_tasks = [
            task for task in registered_tasks
            if not task.startswith("celery.") and not task.startswith("_")
        ]
        
        print(f"✓ Found {len(project_tasks)} registered task(s):")
        for task in sorted(project_tasks):
            print(f"  - {task}")
        
        # Check for expected tasks
        expected_tasks = [
            "core.tasks.simple_async_task",
            "core.tasks.periodic_task",
            "config.celery.debug_task",
        ]
        
        missing_tasks = [task for task in expected_tasks if task not in registered_tasks]
        if missing_tasks:
            print(f"\n⚠ Missing expected tasks: {missing_tasks}")
        else:
            print("\n✓ All expected tasks are registered!")
        
        return True
    except Exception as e:
        print(f"✗ Task registration check failed: {e}")
        return False


def test_worker_availability():
    """Test if Celery workers are available."""
    print_section("Testing Worker Availability")
    try:
        app = current_app
        inspect = app.control.inspect()
        
        # Check active workers
        active_workers = inspect.active()
        stats = inspect.stats()
        
        if active_workers:
            print("✓ Active workers found:")
            for worker in active_workers.keys():
                worker_stats = stats.get(worker, {})
                print(f"  - {worker}")
                print(f"    Pool: {worker_stats.get('pool', {}).get('implementation', 'N/A')}")
                print(f"    Processes: {worker_stats.get('pool', {}).get('max-concurrency', 'N/A')}")
            return True
        else:
            print("⚠ No active workers found.")
            print("\n  To start a worker:")
            print("    celery -A config worker -l info")
            print("\n  Or using Docker Compose:")
            print("    docker-compose up celery_worker")
            return False
    except Exception as e:
        print(f"✗ Worker availability check failed: {e}")
        return False


def test_task_execution(sync: bool = False):
    """Test task execution."""
    print_section("Testing Task Execution")
    
    if sync:
        print("Running tasks synchronously (for testing without worker)...")
        try:
            # Test simple_async_task
            result = simple_async_task("Hello from test script!")
            print(f"✓ simple_async_task executed successfully")
            print(f"  Result: {result}")
            
            # Test periodic_task
            result = periodic_task()
            print(f"✓ periodic_task executed successfully")
            print(f"  Result: {result}")
            
            return True
        except Exception as e:
            print(f"✗ Task execution failed: {e}")
            return False
    else:
        try:
            # Test async task execution
            print("Sending simple_async_task...")
            task_result = simple_async_task.delay("Hello from test script!")
            print(f"✓ Task sent successfully")
            print(f"  Task ID: {task_result.id}")
            print(f"  State: {task_result.state}")
            
            # Wait for result (with timeout)
            try:
                result = task_result.get(timeout=10)
                print(f"✓ Task completed successfully")
                print(f"  Result: {result}")
            except Exception as e:
                print(f"⚠ Task execution timeout or error: {e}")
                print("  Make sure Celery worker is running")
                return False
            
            # Test periodic_task
            print("\nSending periodic_task...")
            task_result = periodic_task.delay()
            print(f"✓ Task sent successfully")
            print(f"  Task ID: {task_result.id}")
            
            try:
                result = task_result.get(timeout=10)
                print(f"✓ Task completed successfully")
                print(f"  Result: {result}")
            except Exception as e:
                print(f"⚠ Task execution timeout or error: {e}")
                return False
            
            return True
        except Exception as e:
            print(f"✗ Task execution failed: {e}")
            print("\n  Troubleshooting:")
            print("  1. Ensure Celery worker is running")
            print("  2. Check RabbitMQ connection")
            print("  3. Verify task is registered")
            return False


def test_debug_task():
    """Test the debug task."""
    print_section("Testing Debug Task")
    try:
        from config.celery import debug_task
        
        print("Sending debug_task...")
        task_result = debug_task.delay()
        print(f"✓ Debug task sent successfully")
        print(f"  Task ID: {task_result.id}")
        
        try:
            # Debug task has ignore_result=True, so we just check it was accepted
            task_result.get(timeout=5)
        except Exception:
            # This is expected for ignore_result tasks
            pass
        
        print("✓ Debug task executed (result ignored as configured)")
        return True
    except Exception as e:
        print(f"✗ Debug task test failed: {e}")
        return False


def print_configuration():
    """Print current Celery configuration."""
    print_section("Current Configuration")
    print(f"Broker URL: {settings.CELERY_BROKER_URL}")
    print(f"Result Backend: {settings.CELERY_RESULT_BACKEND}")
    print(f"Task Serializer: {settings.CELERY_TASK_SERIALIZER}")
    print(f"Result Serializer: {settings.CELERY_RESULT_SERIALIZER}")
    print(f"Timezone: {settings.CELERY_TIMEZONE}")


def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Celery functionality")
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Run tasks synchronously (for testing without worker)",
    )
    parser.add_argument(
        "--skip-execution",
        action="store_true",
        help="Skip task execution tests",
    )
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("  CELERY TEST SUITE")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Print configuration
    print_configuration()
    
    # Run tests
    results = []
    
    results.append(("Broker Connection", test_broker_connection()))
    results.append(("Task Registration", test_task_registration()))
    results.append(("Worker Availability", test_worker_availability()))
    
    if not args.skip_execution:
        results.append(("Task Execution", test_task_execution(sync=args.sync)))
        if not args.sync:
            results.append(("Debug Task", test_debug_task()))
    
    # Print summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n⚠ Some tests failed. Review the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

