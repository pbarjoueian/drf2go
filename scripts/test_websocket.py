#!/usr/bin/env python
"""
Test script for WebSocket functionality.

This script tests:
- WebSocket connection to the server
- Message sending and receiving
- Connection handling
- Error handling

Usage:
    python scripts/test_websocket.py
    python scripts/test_websocket.py --url ws://localhost:8000/ws/simple/
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime

try:
    import websockets
except ImportError:
    print("Error: 'websockets' library is required for WebSocket testing.")
    print("Install it with: pip install websockets")
    sys.exit(1)


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_message(message_type: str, data: dict):
    """Print a formatted message."""
    print(f"\n[{message_type}]")
    print(json.dumps(data, indent=2))


async def test_websocket_connection(url: str, timeout: int = 10):
    """Test WebSocket connection and basic messaging."""
    print_section("Testing WebSocket Connection")

    try:
        print(f"Connecting to: {url}")

        async with websockets.connect(
            url, ping_interval=None, ping_timeout=timeout
        ) as websocket:
            print("✓ Connection established!")

            # Wait for initial connection message
            try:
                initial_message = await asyncio.wait_for(
                    websocket.recv(), timeout=timeout
                )
                initial_data = json.loads(initial_message)
                print_message("CONNECTION MESSAGE", initial_data)

                if initial_data.get("type") == "connection":
                    print("✓ Received expected connection message")
                else:
                    print("⚠ Unexpected connection message format")
            except TimeoutError:
                print("⚠ No initial connection message received")
            except json.JSONDecodeError as e:
                print(f"⚠ Failed to parse initial message: {e}")
                print(f"  Raw message: {initial_message}")

            # Test sending and receiving messages
            test_messages = [
                {"message": "Hello, WebSocket!"},
                {"message": "Test message 1"},
                {"message": "Test message 2"},
            ]

            print_section("Testing Message Exchange")

            for i, test_msg in enumerate(test_messages, 1):
                print(f"\n--- Test Message {i} ---")
                print(f"Sending: {test_msg}")

                # Send message
                await websocket.send(json.dumps(test_msg))
                print("✓ Message sent")

                # Receive response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                    response_data = json.loads(response)
                    print_message("RESPONSE", response_data)

                    if response_data.get("type") == "message":
                        expected_echo = f"Echo: {test_msg['message']}"
                        if response_data.get("message") == expected_echo:
                            print("✓ Received correct echo response")
                        else:
                            print(f"⚠ Unexpected echo: expected '{expected_echo}'")
                    else:
                        print(
                            f"⚠ Unexpected response type: {response_data.get('type')}"
                        )
                except TimeoutError:
                    print("✗ Timeout waiting for response")
                    return False
                except json.JSONDecodeError as e:
                    print(f"✗ Failed to parse response: {e}")
                    print(f"  Raw response: {response}")
                    return False

            # Test invalid JSON handling
            print_section("Testing Error Handling")
            print("\nSending invalid JSON...")
            await websocket.send("This is not valid JSON")

            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                response_data = json.loads(response)
                print_message("ERROR RESPONSE", response_data)

                if response_data.get("type") == "error":
                    print("✓ Server correctly handled invalid JSON")
                else:
                    print("⚠ Unexpected error response format")
            except TimeoutError:
                print("⚠ No error response received")

            print("\n✓ WebSocket test completed successfully!")
            return True

    except websockets.exceptions.InvalidURI as e:
        print(f"✗ Invalid WebSocket URL: {e}")
        return False
    except websockets.exceptions.ConnectionClosed as e:
        print(f"✗ Connection closed unexpectedly: {e}")
        return False
    except ConnectionRefusedError:
        print("✗ Connection refused. Is the server running?")
        print("\n  Start the server with:")
        print("    python manage.py runserver")
        print("  Or using Docker Compose:")
        print("    make up  (starts the web service)")
        return False
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\n  Troubleshooting:")
        print("  1. Verify server is running and accessible")
        print("  2. Check WebSocket URL is correct")
        print("  3. Ensure Redis is running (if using Redis channel layer)")
        print("  4. Check server logs for errors")
        return False


async def test_multiple_connections(url: str, num_connections: int = 3):
    """Test multiple concurrent WebSocket connections."""
    print_section(f"Testing Multiple Connections ({num_connections})")

    async def single_connection_test(connection_id: int):
        """Test a single connection."""
        try:
            async with websockets.connect(url, ping_interval=None) as websocket:
                # Wait for connection message
                await asyncio.wait_for(websocket.recv(), timeout=5)

                # Send a test message
                test_msg = {"message": f"Hello from connection {connection_id}"}
                await websocket.send(json.dumps(test_msg))

                # Receive response
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                json.loads(response)

                print(f"  ✓ Connection {connection_id}: Success")
                return True
        except Exception as e:
            print(f"  ✗ Connection {connection_id}: Failed - {e}")
            return False

    # Create multiple concurrent connections
    tasks = [single_connection_test(i) for i in range(1, num_connections + 1)]
    results = await asyncio.gather(*tasks)

    passed = sum(results)
    print(f"\nResults: {passed}/{num_connections} connections successful")

    return passed == num_connections


def print_configuration(url: str):
    """Print current WebSocket configuration."""
    print_section("Configuration")
    print(f"WebSocket URL: {url}")
    print("Protocol: WebSocket (WS)")


def main():
    """Main test function."""
    parser = argparse.ArgumentParser(description="Test WebSocket functionality")
    parser.add_argument(
        "--url",
        default="ws://localhost:8000/ws/simple/",
        help="WebSocket URL to connect to (default: ws://localhost:8000/ws/simple/)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Timeout in seconds for operations (default: 10)",
    )
    parser.add_argument(
        "--multi",
        type=int,
        metavar="N",
        help="Test multiple concurrent connections (specify number)",
    )
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("  WEBSOCKET TEST SUITE")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Print configuration
    print_configuration(args.url)

    # Run tests
    results = []

    # Basic connection test
    result = asyncio.run(test_websocket_connection(args.url, args.timeout))
    results.append(("Basic Connection", result))

    # Multiple connections test (if requested)
    if args.multi:
        result = asyncio.run(test_multiple_connections(args.url, args.multi))
        results.append((f"Multiple Connections ({args.multi})", result))

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
