# Tribe — Ops Excellence Pack

## Service Dependency Map

```
Client Requests
    ↓
Kubernetes Ingress (/api → port 8001)
    ↓
Next.js API Server (port 3000)
    ├── MongoDB (port 27017) — primary data store
    ├── Redis (port 6379) — cache layer
    ├── Object Storage (Emergent S3) — media files
    └── Moderation Service (port 8002) — AI safety
```

## Monitoring Endpoints

| Endpoint | Purpose | Alert Threshold |
|----------|---------|-----------------|
| `GET /api/healthz` | Basic liveness | Non-200 for >30s |
| `GET /api/readyz` | DB connectivity | Non-200 for >10s |
| `GET /api/ops/health` | All dependencies | `status: degraded` for >60s |
| `GET /api/ops/metrics` | Business metrics | Custom per metric |
| `GET /api/cache/stats` | Cache performance | hitRate < 30% |
| `GET /api/ops/backup-check` | Backup readiness | `backupReady: false` |

## SLO Targets

| Service | Metric | Target | Measurement |
|---------|--------|--------|-------------|
| API | Availability | 99.9% | healthz check every 30s |
| API | p50 latency | < 300ms | load test results |
| API | p95 latency | < 500ms | load test results |
| API | p99 latency | < 800ms | load test results |
| Login | p50 latency | < 1500ms | PBKDF2 by design |
| Cache | Hit rate | > 40% | /cache/stats |
| Moderation | Availability | 99% | ops/health check |

## Error Budget

Monthly error budget at 99.9% SLO:
- **43 minutes** downtime per month
- **4.3 minutes** per day max
- Alert if >50% consumed in first half of month

## Incident Runbook

### Scenario 1: API Not Responding

```bash
# Check process
sudo supervisorctl status
# Check logs
tail -100 /var/log/supervisor/backend.err.log
# Restart
sudo supervisorctl restart backend
```

### Scenario 2: MongoDB Down

```bash
# Check connection
mongosh --eval "db.adminCommand('ping')"
# Check disk space
df -h
# Restart MongoDB
sudo systemctl restart mongod
# Verify recovery
curl /api/readyz
```

### Scenario 3: Redis Down (Non-Critical — Fallback Active)

```bash
# Check status
redis-cli ping
# Restart
redis-server --daemonize yes --port 6379
# Verify reconnection (may need app restart for full reconnect)
curl /api/cache/stats
# Redis down = fallback to in-memory cache (no data loss, slight performance hit)
```

### Scenario 4: Moderation Service Down (Non-Critical — Keyword Fallback)

```bash
# Check
curl http://localhost:8002/health
# Restart
cd /app && EMERGENT_LLM_KEY=<key> nohup python3 services/moderation-service.py > /var/log/moderation.log 2>&1 &
# Verify
curl http://localhost:8002/health
# Service down = keyword-only moderation (reduced but still active safety net)
```

### Scenario 5: Object Storage Unavailable

```bash
# Check via health endpoint
curl /api/ops/health | jq .checks.objectStorage
# Behavior: uploads fall back to base64-in-MongoDB
# No data loss, but uploads will be slower and larger
# Resolution: check Emergent storage service status
```

### Scenario 6: High Latency / Degraded Performance

```bash
# Check cache hit rate
curl /api/cache/stats
# Check active connections
curl /api/ops/metrics
# If cache cold after restart:
#   - Performance will normalize within ~60s as caches warm
# If sustained high latency:
#   - Check MongoDB slow query log
#   - Check Redis memory usage: redis-cli info memory
#   - Check open connections: redis-cli info clients
```

### Scenario 7: Abuse / Spam Wave

```bash
# Check rate limiting
# Current: 120 req/min per IP
# Check moderation queue
curl /api/admin/stats  # openReports count
# Emergency: reduce rate limit in route.js
# RATE_LIMIT_MAX = 30  # temporarily aggressive
# Restart server after change
```

## Backup & Restore

### Backup

```bash
# Full backup
mongodump --db=your_database_name --out=/backup/$(date +%Y%m%d_%H%M%S)

# Backup specific collections
mongodump --db=your_database_name --collection=users --out=/backup/users_$(date +%s)

# Redis backup (if data matters)
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb /backup/redis_$(date +%s).rdb
```

### Restore

```bash
# Full restore
mongorestore --db=your_database_name --drop /backup/<timestamp>/your_database_name/

# Verify
curl /api/ops/backup-check
```

### Restore Drill Proof (Executed March 7, 2026)

```bash
# 1. Create backup
mongodump --db=your_database_name --out=/tmp/drill_backup

# 2. Drop a non-critical collection
mongosh --eval 'db.feature_flags.drop()' your_database_name

# 3. Verify missing
curl /api/ops/backup-check  # collection count should be 24

# 4. Restore
mongorestore --db=your_database_name /tmp/drill_backup/your_database_name/ --drop

# 5. Verify restored
curl /api/ops/backup-check  # collection count should be 25
```

## Secret Rotation

### Emergent LLM Key Rotation

```bash
# 1. Get new key from Emergent dashboard
# 2. Update .env
EMERGENT_LLM_KEY=<new_key>
# 3. Restart moderation service
kill $(pgrep -f moderation-service)
cd /app && nohup python3 services/moderation-service.py > /var/log/moderation.log 2>&1 &
# 4. Verify
curl http://localhost:8002/config  # apiAvailable should be true
```

### Failure Simulation: Invalid Key

```bash
# If key becomes invalid:
# - Moderation service returns keyword-only results (degraded, not broken)
# - Object storage uploads fall back to base64
# - No hard failure, graceful degradation
```

## Dependency Failure Matrix

| Dependency Down | Impact | Mitigation |
|----------------|--------|------------|
| MongoDB | CRITICAL — all reads/writes fail | Restart DB, restore from backup |
| Redis | LOW — fallback to in-memory cache | Auto-fallback active, restart Redis |
| Moderation Service | LOW — keyword filter active | Auto-fallback, restart service |
| Object Storage | MEDIUM — media uploads slower | Auto-fallback to base64 in MongoDB |
| All dependencies | | API still responds with degraded status |

## Redis Failover Test Results (March 7, 2026)

| Phase | Action | Result |
|-------|--------|--------|
| 1 | Redis running, hit endpoints | Cache populated, hits increasing |
| 2 | `redis-cli shutdown` | Redis stopped |
| 3 | Hit same endpoints | API responds normally, in-memory fallback active |
| 4 | `redis-server --daemonize yes` | Redis restarted |
| 5 | App restart → cache stats | `redis.status: connected`, keys: 0 (cold cache) |
| 6 | Hit endpoints | Cache repopulated via Redis |

**Result: ZERO downtime during Redis failover. Graceful degradation confirmed.**
