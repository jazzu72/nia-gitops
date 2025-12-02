# Nia: Debug & Run Guide

## Quick Start

### Prerequisites
- Python 3.9+ installed
- Virtual environment (`venv`)
- Git for version control
- PowerShell or Bash shell

### 1. First-Time Setup

```bash
# Clone the repository
git clone https://github.com/jazzu72/nia-gitops.git
cd nia-gitops

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development tools (optional but recommended)
pip install pytest pytest-cov pdbpp ipython
```

---

## Running Nia Locally

### Option 1: Simple Development Mode (Recommended for First Run)

```bash
# Activate venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start Nia with hot-reload
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

**Test the server:**
```bash
# In another terminal:
curl http://localhost:8000/health

# Expected response:
# {"status": "ok", "timestamp": 1734123456.789}
```

### Option 2: Production-Like Mode (Multi-Worker)

```bash
# Start with 4 worker processes
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info

# For CPU-optimized worker count:
# Formula: (2 * NUM_CPU_CORES) + 1
# Example: If you have 2 cores: (2 * 2) + 1 = 5 workers
```

### Option 3: One-Command Dev Startup (Using Script)

Create a `scripts/dev.sh` file in your project:

```bash
#!/bin/bash
set -e

echo "🚀 Starting Nia development environment..."

# Activate venv
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt

# Start Nia
echo "✅ Nia running at http://localhost:8000"
echo "📝 Logs available at nia.log"
uvicorn app:app --host 0.0.0.0 --port 8000 --reload --log-level info > nia.log 2>&1 &
echo "PID: $!"

# Keep script running
wait
```

**Run it:**
```bash
chmod +x scripts/dev.sh
./scripts/dev.sh
```

---

## Debugging Nia

### 1. Check Application Logs

```bash
# View real-time logs
tail -f nia.log

# View specific error patterns
grep "ERROR" nia.log | tail -20

# Watch for performance warnings
grep "took.*ms" nia.log | tail -10
```

### 2. Using Python Debugger (pdb)

#### Add breakpoint in code:
```python
# In your app.py or webhook handler:
async def handle_sms_webhook(request):
    data = await request.json()
    
    # Breakpoint - execution will pause here
    breakpoint()  # or: import pdb; pdb.set_trace()
    
    # Process data
    result = await brain.think(data)
    return result
```

**Commands in debugger:**
```
n        - Next line
s        - Step into function
c        - Continue execution
l        - List current code
p var    - Print variable
h        - Help
q        - Quit debugger
```

#### Better debugging with pdb++:
```bash
pip install pdbpp
# Use `breakpoint()` as above, pdb++ will be automatically used
# Adds: syntax highlighting, better repr, smart command completion
```

### 3. Enhanced Debugging with ipython

```bash
pip install ipython

# In your code:
from IPython import embed
embed()  # Drops you into ipython shell at this point
```

### 4. Request/Response Logging

Add to your Nia app for detailed request tracing:

```python
# app.py
import logging
from fastapi import FastAPI, Request
import json
import time

app = FastAPI()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and responses."""
    start_time = time.time()
    
    # Log request
    body = await request.body()
    logger.info(f"[REQUEST] {request.method} {request.url.path}")
    if body:
        try:
            logger.debug(f"[REQUEST BODY] {json.loads(body)}")
        except:
            logger.debug(f"[REQUEST BODY] {body[:200]}")  # First 200 chars
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"[RESPONSE] {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time*1000:.2f}ms")
    
    return response
```

### 5. Performance Profiling

#### Simple timing profiler:
```python
# scripts/profile_endpoints.py
import asyncio
import httpx
import time
from statistics import mean, stdev

async def profile_endpoint(url: str, name: str, num_requests: int = 50):
    """Profile a single endpoint."""
    times = []
    errors = 0
    
    async with httpx.AsyncClient() as client:
        print(f"\n📊 Profiling {name}...")
        for i in range(num_requests):
            try:
                start = time.perf_counter()
                response = await client.get(url, timeout=10.0)
                elapsed = (time.perf_counter() - start) * 1000  # ms
                
                if response.status_code == 200:
                    times.append(elapsed)
                else:
                    errors += 1
                    print(f"  ⚠️  Request {i+1}: Status {response.status_code}")
            except Exception as e:
                errors += 1
                print(f"  ❌ Request {i+1}: {e}")
    
    if times:
        print(f"  ✅ Successful: {len(times)}/{num_requests}")
        print(f"  ⏱️  Mean: {mean(times):.2f}ms")
        print(f"  📈 Stdev: {stdev(times):.2f}ms" if len(times) > 1 else "")
        print(f"  🔻 Min: {min(times):.2f}ms")
        print(f"  🔺 Max: {max(times):.2f}ms")
        print(f"  ❌ Errors: {errors}")

async def main():
    # Test your endpoints
    await profile_endpoint("http://localhost:8000/health", "Health Check")
    await profile_endpoint("http://localhost:8000/sms/webhook", "SMS Webhook")
    await profile_endpoint("http://localhost:8000/email/webhook", "Email Webhook")

if __name__ == "__main__":
    asyncio.run(main())
```

**Run it:**
```bash
python scripts/profile_endpoints.py
```

---

## Common Issues & Solutions

### Issue: Port 8000 Already in Use

```bash
# Find process using port 8000
# On macOS/Linux:
lsof -i :8000

# On Windows (PowerShell):
netstat -ano | findstr :8000

# Kill the process
# On macOS/Linux:
kill -9 <PID>

# On Windows:
taskkill /PID <PID> /F

# Or use a different port:
uvicorn app:app --port 8001
```

### Issue: Module Not Found

```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# Check installed packages
pip list
```

### Issue: Webhook Not Receiving Data

**Check incoming requests are reaching Nia:**
```bash
# Enable detailed logging
uvicorn app:app --log-level debug

# Monitor with ngrok (for external webhooks)
pip install ngrok-py
# Create tunnel: ngrok http 8000
# Forward your external service to the ngrok URL
```

### Issue: Brain.think() Times Out

```python
# Add timeout handling
from asyncio import timeout

@app.post("/brain/query")
async def query_brain(query: dict):
    try:
        async with timeout(5):  # 5 second timeout
            result = await brain.think(query)
        return result
    except TimeoutError:
        logger.error("Brain.think() exceeded 5s timeout")
        return {"error": "Brain query timeout", "code": "TIMEOUT"}
```

---

## Testing Webhooks Locally

### 1. Using curl for Manual Testing

```bash
# SMS Webhook
curl -X POST http://localhost:8000/sms/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+1234567890",
    "body": "Hello from test",
    "message_sid": "test_msg_123"
  }'

# Email Webhook
curl -X POST http://localhost:8000/email/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "from": "sender@example.com",
    "subject": "Test Email",
    "body": "Test email content",
    "message_id": "test_email_123"
  }'
```

### 2. Using Postman or Insomnia

- Import webhook JSON payloads into Postman
- Create collections for SMS/Email/Brain endpoints
- Save responses for comparison testing

### 3. Using Python Script for Batch Testing

```python
# scripts/test_webhooks.py
import asyncio
import httpx
import json

async def test_sms_webhook():
    async with httpx.AsyncClient() as client:
        payload = {
            "from": "+19876543210",
            "body": "Test message from batch script",
            "message_sid": f"test_batch_{int(time.time())}"
        }
        response = await client.post(
            "http://localhost:8000/sms/webhook",
            json=payload
        )
        print(f"SMS Webhook Response: {response.status_code}")
        print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    asyncio.run(test_sms_webhook())
```

---

## Performance Tuning Checklist

- [ ] Running with multiple workers? (`--workers 4` or more)
- [ ] Using uvloop for faster event loop? (`pip install uvloop`)
- [ ] Using httptools for faster HTTP parsing? (`pip install httptools`)
- [ ] Connection pooling enabled for databases?
- [ ] Caching implemented for repeated brain queries?
- [ ] All I/O operations using async/await?
- [ ] Health check endpoint added? (`/health`)
- [ ] Monitoring logs for slow requests?
- [ ] Load testing performed? (see profile script)
- [ ] Environment variables properly configured?

---

## Production Readiness

Before deploying to production, ensure:

1. **Environment Variables Set**
   ```bash
   NIA_ENV=production
   NIA_LOG_LEVEL=info
   NIA_WORKERS=8
   NIA_DB_POOL_SIZE=20
   ```

2. **SSL/TLS Configured**
   ```bash
   # Use reverse proxy (nginx) or:
   uvicorn app:app --ssl-keyfile=/path/to/key.pem --ssl-certfile=/path/to/cert.pem
   ```

3. **Rate Limiting Enabled**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   ```

4. **Error Monitoring Set Up**
   ```python
   import sentry_sdk
   sentry_sdk.init("YOUR_SENTRY_DSN")
   ```

5. **Metrics Exported**
   ```python
   from prometheus_client import Counter, Histogram
   webhook_counter = Counter('nia_webhooks', 'Webhook count')
   ```

---

## Useful Commands Reference

```bash
# Start Nia
uvicorn app:app --reload

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app

# Format code
black app.py

# Lint
flake8 app.py

# Type check
mypy app.py

# Check dependencies
pip check

# Update all packages
pip list --outdated
pip install --upgrade -r requirements.txt

# Generate requirements.txt from current env
pip freeze > requirements.txt
```

---

## Next Steps

1. **This Session:** Get Nia running locally with `./scripts/dev.sh`
2. **Before Pushing:** Run tests and apply optimizations from `OPTIMIZATION_SUGGESTIONS.md`
3. **In Production:** Enable monitoring, rate limiting, and error tracking

---

**Last Updated:** 2025-12-01
**Maintainer:** House of Jazzu
**Questions?** Check GitHub Issues or Discussions
