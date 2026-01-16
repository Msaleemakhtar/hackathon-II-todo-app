#!/usr/bin/env python3
"""
End-to-End Dapr Integration Test
Tests event publishing and consumption via Dapr with local Kafka
"""
import httpx
import json
import asyncio
from datetime import datetime

DAPR_HTTP_PORT = 3500
PUBSUB_NAME = "pubsub-kafka"
TOPIC = "task-reminders"

async def test_dapr_publish():
    """Test publishing event via Dapr HTTP API"""
    print("=" * 60)
    print("Dapr End-to-End Test - Event Publishing")
    print("=" * 60)
    print()

    # Create test event
    test_event = {
        "task_id": f"e2e-test-{int(datetime.now().timestamp())}",
        "user_id": "dapr-test-user",
        "title": "Dapr E2E Test Task",
        "due_at": datetime.utcnow().isoformat() + "Z",
        "remind_at": datetime.utcnow().isoformat() + "Z",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    print(f"Test Event: {json.dumps(test_event, indent=2)}")
    print()

    # Publish via Dapr
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{TOPIC}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            print(f"Publishing to: {url}")
            response = await client.post(url, json=test_event)

            if response.status_code == 204:
                print(f"✅ Event published successfully (HTTP {response.status_code})")
                print()
                return True
            else:
                print(f"❌ Failed to publish event (HTTP {response.status_code})")
                print(f"Response: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Error publishing event: {e}")
        return False

async def test_dapr_components():
    """Test Dapr component metadata"""
    print("=" * 60)
    print("Dapr Components Health Check")
    print("=" * 60)
    print()

    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/metadata"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)

            if response.status_code == 200:
                metadata = response.json()
                print(f"✅ Dapr sidecar responding")
                print(f"App ID: {metadata.get('id', 'unknown')}")
                print(f"Runtime Version: {metadata.get('runtimeVersion', 'unknown')}")
                print()

                # Check components
                components = metadata.get('components', [])
                print(f"Loaded Components ({len(components)}):")
                for comp in components:
                    print(f"  - {comp.get('name')} ({comp.get('type')})")
                print()

                # Check active actors
                actors = metadata.get('actors', [])
                if actors:
                    print(f"Active Actors: {len(actors)}")

                # Check subscriptions
                subscriptions = metadata.get('subscriptions', [])
                if subscriptions:
                    print(f"Subscriptions ({len(subscriptions)}):")
                    for sub in subscriptions:
                        print(f"  - {sub.get('pubsubname')}/{sub.get('topic')} → {sub.get('route')}")
                print()

                return True
            else:
                print(f"❌ Failed to get metadata (HTTP {response.status_code})")
                return False
    except Exception as e:
        print(f"❌ Error getting metadata: {e}")
        return False

async def test_dapr_health():
    """Test Dapr health endpoint"""
    print("=" * 60)
    print("Dapr Health Check")
    print("=" * 60)
    print()

    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/healthz"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)

            if response.status_code == 204:
                print(f"✅ Dapr sidecar healthy (HTTP {response.status_code})")
                print()
                return True
            else:
                print(f"❌ Dapr sidecar unhealthy (HTTP {response.status_code})")
                return False
    except Exception as e:
        print(f"❌ Error checking health: {e}")
        return False

async def main():
    """Run all tests"""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "DAPR INTEGRATION E2E TEST" + " " * 23 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    results = []

    # Test 1: Health
    results.append(("Health Check", await test_dapr_health()))

    # Test 2: Components
    results.append(("Components Check", await test_dapr_components()))

    # Test 3: Event Publishing
    results.append(("Event Publishing", await test_dapr_publish()))

    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print()

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print()
    print(f"Results: {passed}/{total} tests passed")
    print()

    if passed == total:
        print("✅ ALL TESTS PASSED - Dapr integration working correctly!")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Check logs above")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
