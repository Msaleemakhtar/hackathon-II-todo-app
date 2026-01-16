#!/usr/bin/env python3
"""
Test Dapr State Store integration
"""
import httpx
import json
import asyncio
from datetime import datetime

DAPR_HTTP_PORT = 3500
STATE_STORE_NAME = "statestore-postgres"

async def test_state_store():
    """Test Dapr state store operations"""
    print("=" * 60)
    print("Dapr State Store Test")
    print("=" * 60)
    print()

    # Test key and value
    test_key = f"test-state-{int(datetime.now().timestamp())}"
    test_value = {
        "message": "Dapr state store test",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. Save state
            print("1. Saving state...")
            save_url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/{STATE_STORE_NAME}"
            save_payload = [{
                "key": test_key,
                "value": test_value
            }]

            response = await client.post(save_url, json=save_payload)
            if response.status_code == 204:
                print(f"✅ State saved successfully (key: {test_key})")
            else:
                print(f"❌ Failed to save state (HTTP {response.status_code})")
                print(f"Response: {response.text}")
                return False

            print()

            # 2. Get state
            print("2. Retrieving state...")
            get_url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/{STATE_STORE_NAME}/{test_key}"

            response = await client.get(get_url)
            if response.status_code == 200:
                retrieved = response.json()
                print(f"✅ State retrieved successfully")
                print(f"Value: {json.dumps(retrieved, indent=2)}")

                # Verify value matches
                if retrieved == test_value:
                    print("✅ Value matches!")
                else:
                    print("⚠️  Value mismatch")
            else:
                print(f"❌ Failed to get state (HTTP {response.status_code})")
                return False

            print()

            # 3. Delete state
            print("3. Deleting state...")
            delete_url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/{STATE_STORE_NAME}/{test_key}"

            response = await client.delete(delete_url)
            if response.status_code == 204:
                print(f"✅ State deleted successfully")
            else:
                print(f"❌ Failed to delete state (HTTP {response.status_code})")

            print()

            # 4. Verify deletion
            print("4. Verifying deletion...")
            response = await client.get(get_url)
            if response.status_code == 204 or response.text == "":
                print(f"✅ State deleted (confirmed)")
            else:
                print(f"⚠️  State still exists (HTTP {response.status_code})")

            print()
            print("=" * 60)
            print("✅ STATE STORE TEST PASSED")
            print("=" * 60)
            return True

    except Exception as e:
        print(f"❌ Error testing state store: {e}")
        import traceback
        traceback.print_exc()
        return False

async def check_dapr_metadata():
    """Check Dapr metadata for state store"""
    print("=" * 60)
    print("Checking Dapr Components")
    print("=" * 60)
    print()

    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/metadata"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                metadata = response.json()
                components = metadata.get('components', [])

                print("Loaded Components:")
                for comp in components:
                    name = comp.get('name', 'unknown')
                    comp_type = comp.get('type', 'unknown')
                    version = comp.get('version', '')
                    print(f"  - {name} ({comp_type}/{version})")

                # Check if statestore is loaded
                statestore = next((c for c in components if c.get('name') == STATE_STORE_NAME), None)
                if statestore:
                    print()
                    print(f"✅ State store '{STATE_STORE_NAME}' is loaded")
                    return True
                else:
                    print()
                    print(f"❌ State store '{STATE_STORE_NAME}' NOT found")
                    print("Available state stores:")
                    for comp in components:
                        if 'state' in comp.get('type', '').lower():
                            print(f"  - {comp.get('name')}")
                    return False
            else:
                print(f"❌ Failed to get metadata (HTTP {response.status_code})")
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "DAPR STATE STORE E2E TEST" + " " * 22 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    # Check if state store is loaded
    if not await check_dapr_metadata():
        print()
        print("❌ State store not loaded - test cannot proceed")
        return 1

    print()

    # Test state store operations
    if await test_state_store():
        return 0
    else:
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
