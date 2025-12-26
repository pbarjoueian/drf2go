# Test Scripts

This directory contains utility scripts for testing various components of the application.

## Available Scripts

### `test_celery.py`

Tests Celery functionality including:

- RabbitMQ broker connection
- Task registration and discovery
- Task execution (async and sync)
- Worker availability
- Debug task execution

#### Usage

```bash
# Basic test (requires Celery worker to be running)
python scripts/test_celery.py

# Test without worker (runs tasks synchronously)
python scripts/test_celery.py --sync

# Skip task execution tests
python scripts/test_celery.py --skip-execution
```

#### Prerequisites

- RabbitMQ service running
- Celery worker running (unless using `--sync` flag)
- Django environment configured

#### Example Output

```
======================================================================
  CELERY TEST SUITE
======================================================================
Started at: 2024-01-15 10:30:00

======================================================================
  Current Configuration
======================================================================
Broker URL: amqp://guest:guest@rabbitmq:5672//
Result Backend: rpc://
...

✓ All tests passed!
```

### `test_websocket.py`

Tests WebSocket functionality including:

- WebSocket connection establishment
- Message sending and receiving
- Echo functionality
- Error handling (invalid JSON)
- Multiple concurrent connections

#### Usage

```bash
# Basic test with default URL
python scripts/test_websocket.py

# Test with custom URL
python scripts/test_websocket.py --url ws://localhost:8000/ws/simple/

# Test multiple concurrent connections
python scripts/test_websocket.py --multi 5

# Custom timeout
python scripts/test_websocket.py --timeout 30
```

#### Prerequisites

- Django server running (with Daphne/ASGI)
- Redis service running (if using Redis channel layer)
- `websockets` library installed: `pip install websockets`

#### Example Output

```
======================================================================
  WEBSOCKET TEST SUITE
======================================================================
Started at: 2024-01-15 10:30:00

======================================================================
  Configuration
======================================================================
WebSocket URL: ws://localhost:8000/ws/simple/
Protocol: WebSocket (WS)

✓ Connection established!
✓ All tests passed!
```

## Installation

Install development dependencies (including `websockets`):

```bash
pip install -r requirements-dev.txt
```

Or using pipenv:

```bash
pipenv install --dev
```

## Running Tests

### Quick Test

Test both Celery and WebSocket:

```bash
# Terminal 1: Start services
docker-compose up -d rabbitmq redis

# Terminal 2: Start Celery worker
celery -A config worker -l info

# Terminal 3: Start Django server
python manage.py runserver

# Terminal 4: Run tests
python scripts/test_celery.py
python scripts/test_websocket.py
```

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# Run Celery test (from host)
python scripts/test_celery.py

# Run WebSocket test (from host)
python scripts/test_websocket.py

# Or run tests inside container
docker-compose exec web python scripts/test_celery.py
docker-compose exec web python scripts/test_websocket.py
```

## Troubleshooting

### Celery Tests Fail

1. **Broker Connection Failed**
   - Verify RabbitMQ is running: `docker-compose ps rabbitmq`
   - Check `CELERY_BROKER_URL` in settings
   - Verify RabbitMQ credentials

2. **No Active Workers**
   - Start Celery worker: `celery -A config worker -l info`
   - Or use Docker Compose: `docker-compose up celery_worker`

3. **Task Execution Timeout**
   - Ensure worker is running and processing tasks
   - Check worker logs for errors
   - Verify task is registered: `celery -A config inspect registered`

### WebSocket Tests Fail

1. **Connection Refused**
   - Verify Django server is running
   - Check server is using ASGI (Daphne), not WSGI
   - Ensure port 8000 is accessible

2. **No Response Received**
   - Check Redis is running (if using Redis channel layer)
   - Verify WebSocket routing is configured correctly
   - Review server logs for errors

3. **Import Error: websockets**
   - Install websockets: `pip install websockets`
   - Or install dev requirements: `pip install -r requirements-dev.txt`

## Script Development

When creating new test scripts:

1. Add shebang: `#!/usr/bin/env python`
2. Add project root to Python path
3. Set Django settings module
4. Initialize Django before importing models
5. Use argparse for command-line arguments
6. Provide clear error messages and troubleshooting tips
7. Make scripts executable: `chmod +x scripts/script_name.py`

## Integration with CI/CD

These scripts can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Test Celery
  run: python scripts/test_celery.py --skip-execution

- name: Test WebSocket
  run: |
    python manage.py runserver &
    sleep 5
    python scripts/test_websocket.py
```
