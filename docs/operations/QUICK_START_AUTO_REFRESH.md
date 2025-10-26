# Using the Auto-Refresh Feature - Quick Start Guide

## TL;DR - Can I test without Redis?

**YES!** The Streamlit UI works perfectly fine without Redis. You can simply run:

```bash
streamlit run omf2/omf.py
```

**What happens without Redis:**
- ✅ UI displays and updates normally
- ✅ Manual page refresh works (F5 or Streamlit's rerun)
- ❌ Automatic refresh on MQTT events is disabled
- ℹ️ You'll see a warning in logs: "⚠️ Redis not available"

## Usage Modes

### Mode 1: Basic Testing (No Redis) ✅ RECOMMENDED FOR QUICK TESTING

**When to use:** Quick UI testing, development, viewing static data

**Setup:**
```bash
# Just run Streamlit - no additional setup needed!
streamlit run omf2/omf.py
```

**What works:**
- All UI pages display correctly
- Manual refresh with F5
- Reading existing order/module/sensor data
- Editing configuration

**What doesn't work:**
- Automatic UI refresh when MQTT messages arrive
- Real-time updates without manual refresh

**No errors, no crashes** - the system gracefully degrades.

---

### Mode 2: Full Auto-Refresh (With Redis) 🚀 RECOMMENDED FOR PRODUCTION

**When to use:** Testing auto-refresh, production deployment, real-time MQTT updates

**Setup:**

1. **Start Redis** (choose one method):

   ```bash
   # Option A: Docker (easiest)
   docker run -d -p 6379:6379 --name redis redis:latest

   # Option B: Local installation
   # Ubuntu/Debian:
   sudo apt-get install redis-server && redis-server
   
   # macOS:
   brew install redis && redis-server
   ```

2. **Start the Flask API** (in a separate terminal):
   ```bash
   python -m omf2.backend.api_refresh
   ```
   The API will be available at `http://localhost:5001`

3. **Start Streamlit**:
   ```bash
   streamlit run omf2/omf.py
   ```

**What works:**
- ✅ Everything from Mode 1
- ✅ Automatic UI refresh when MQTT messages arrive
- ✅ Real-time updates (~1 second latency)
- ✅ Pages reload only when relevant data changes

**Verification:**
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG

# Check API is running
curl http://localhost:5001/api/health
# Should return: {"success": true, "status": "ok", "service": "omf2-refresh-api"}
```

---

## Configuration (Optional)

### Environment Variables

Set these if Redis/API are not on localhost:

```bash
export REDIS_URL="redis://localhost:6379/0"
export REFRESH_API_URL="http://localhost:5001"
```

Or create `.streamlit/secrets.toml`:
```toml
REDIS_URL = "redis://localhost:6379/0"
REFRESH_API_URL = "http://localhost:5001"
```

### Default Values (if not configured)

- **REDIS_URL**: `redis://localhost:6379/0`
- **REFRESH_API_URL**: `http://localhost:5001`

---

## Troubleshooting

### "⚠️ Redis not available" in logs

**This is OK!** The system works without Redis, just without auto-refresh.

**To enable auto-refresh:** Follow Mode 2 setup above.

### UI doesn't auto-refresh even with Redis running

**Check:**
1. Is Redis running? `redis-cli ping`
2. Is the API running? `curl http://localhost:5001/api/health`
3. Are MQTT messages being received? Check gateway logs
4. Does the topic match `gateway.yml` refresh_triggers?

### Redis connection errors

**Check:**
- Redis is running: `docker ps` or `systemctl status redis`
- Port 6379 is not blocked by firewall
- REDIS_URL environment variable is correct

---

## Testing Workflow

### Quick UI Test (No Auto-Refresh)
```bash
streamlit run omf2/omf.py
# Test UI, manual refresh with F5
```

### Full Integration Test (With Auto-Refresh)
```bash
# Terminal 1: Start Redis
docker run -d -p 6379:6379 --name redis redis:latest

# Terminal 2: Start API
python -m omf2.backend.api_refresh

# Terminal 3: Start Streamlit
streamlit run omf2/omf.py

# Terminal 4: Publish test MQTT message
mosquitto_pub -h localhost -t "ccu/order/active" -m '{"orderId": "test123"}'

# Watch the UI auto-refresh within ~1 second!
```

---

## Production Deployment

For production, ensure:

1. **Redis is running** (persistent data directory)
   ```bash
   docker run -d \
     -p 6379:6379 \
     -v redis-data:/data \
     --name redis \
     redis:latest redis-server --appendonly yes
   ```

2. **API is running** (use systemd, supervisor, or container)
   ```bash
   # Example with gunicorn (production WSGI server)
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5001 omf2.backend.api_refresh:app
   ```

3. **Configure URLs** in secrets or environment
   ```bash
   export REDIS_URL="redis://production-redis:6379/0"
   export REFRESH_API_URL="http://production-api:5001"
   ```

---

## Summary

| Feature | Without Redis | With Redis |
|---------|--------------|------------|
| UI Display | ✅ Yes | ✅ Yes |
| Manual Refresh | ✅ Yes (F5) | ✅ Yes (F5) |
| Auto-Refresh | ❌ No | ✅ Yes (~1s) |
| MQTT Processing | ✅ Yes | ✅ Yes |
| Setup Complexity | 🟢 Simple | 🟡 Moderate |
| Recommended For | Testing, Dev | Production |

**Bottom line:** Start with Mode 1 for quick testing. Add Mode 2 when you need auto-refresh.
