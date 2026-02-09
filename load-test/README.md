# Load Testing for Todo Application

This directory contains load testing configuration and scripts for the Todo application using k6, a modern load testing tool.

## Overview

The load tests simulate **1000 concurrent users** performing realistic CRUD operations on the Todo application to verify performance under sustained load.

### Performance Targets

- **P95 Latency**: < 5 seconds for all operations
- **Error Rate**: < 1%
- **Throughput**: > 100 requests/second

### Test Scenarios

The load test simulates a realistic mix of operations:

1. **Create Task** (40% of requests)
   - Creates new tasks with all Phase 5 Part A fields
   - Includes priority, tags, due_date, recurrence, reminder_offset

2. **List Tasks with Filters** (30% of requests)
   - Retrieves tasks with various filter combinations
   - Tests search, priority filter, tag filter, status filter

3. **Update Task Status** (20% of requests)
   - Updates task status (pending → in_progress → completed)
   - Modifies priority and other fields

4. **Delete Task** (10% of requests)
   - Removes tasks from the system

## Prerequisites

### Install k6

**macOS (Homebrew)**:
```bash
brew install k6
```

**Windows (Chocolatey)**:
```bash
choco install k6
```

**Linux (Debian/Ubuntu)**:
```bash
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

**Docker**:
```bash
docker pull grafana/k6:latest
```

### Application Requirements

Ensure the Todo application is running and accessible:

- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000 (optional)

For cloud testing, set the `BASE_URL` environment variable to your deployed application URL.

## Running Load Tests

### Default Test (1000 users, 5 minutes sustained)

```bash
k6 run load-test.js
```

### Custom VUs and Duration

```bash
# 500 users for 2 minutes
k6 run --vus 500 --duration 2m load-test.js

# 2000 users for 10 minutes
k6 run --vus 2000 --duration 10m load-test.js
```

### Test Against Cloud Deployment

```bash
# Test against Minikube
BASE_URL=http://localhost:30001 k6 run load-test.js

# Test against OKE deployment
BASE_URL=https://todo-app.example.com k6 run load-test.js
```

### Using Docker

```bash
docker run --rm -i \
  -v $(pwd):/scripts \
  -e BASE_URL=http://host.docker.internal:8000 \
  grafana/k6:latest run /scripts/load-test.js
```

## Generating Reports

### JSON Output

```bash
k6 run --out json=results/load-test-results.json load-test.js
```

### HTML Report (requires k6-reporter)

1. Install k6-reporter:
   ```bash
   npm install -g k6-to-junit
   ```

2. Generate JSON results:
   ```bash
   k6 run --out json=results/load-test-results.json load-test.js
   ```

3. Convert to HTML (use external tools like k6-html-reporter):
   ```bash
   npm install -g k6-html-reporter
   k6-html-reporter results/load-test-results.json
   ```

### InfluxDB + Grafana (Advanced)

For real-time monitoring during load tests:

1. Start InfluxDB and Grafana:
   ```bash
   docker-compose -f docker-compose-monitoring.yml up -d
   ```

2. Run k6 with InfluxDB output:
   ```bash
   k6 run --out influxdb=http://localhost:8086/k6 load-test.js
   ```

3. View results in Grafana dashboard at http://localhost:3000

## Test Configuration

### Load Profile (Ramp-up Stages)

The default test uses the following stages:

1. **0-30s**: Ramp up to 100 users
2. **30s-1m**: Ramp up to 500 users
3. **1m-1.5m**: Ramp up to 1000 users
4. **1.5m-6.5m**: Sustain 1000 users (5 minutes)
5. **6.5m-7m**: Ramp down to 500 users
6. **7m-7.5m**: Ramp down to 0 users

**Total Duration**: ~7.5 minutes

### Environment Variables

Customize the test with environment variables:

- `BASE_URL`: Backend API URL (default: `http://localhost:8000`)
- `FRONTEND_URL`: Frontend URL (default: `http://localhost:3000`)
- `ENVIRONMENT`: Environment name for tagging (default: `local`)

Example:
```bash
BASE_URL=https://api.todo.example.com \
ENVIRONMENT=production \
k6 run load-test.js
```

## Interpreting Results

### Key Metrics

k6 outputs comprehensive metrics after each test:

```
checks.........................: 99.85% ✓ 124567      ✗ 234
data_received..................: 45 MB  6.0 MB/s
data_sent......................: 12 MB  1.6 MB/s
http_req_blocked...............: avg=1.23ms   min=0s       med=1ms      max=123ms    p(90)=2ms    p(95)=3ms
http_req_connecting............: avg=0.87ms   min=0s       med=0.5ms    max=98ms     p(90)=1.5ms  p(95)=2ms
http_req_duration..............: avg=2.5s     min=100ms    med=2.1s     max=8.9s     p(90)=4.2s   p(95)=4.8s
  { expected_response:true }...: avg=2.4s     min=100ms    med=2.0s     max=7.5s     p(90)=4.0s   p(95)=4.6s
http_req_failed................: 0.15%  ✓ 234         ✗ 124567
http_req_receiving.............: avg=45.67ms  min=10ms     med=40ms     max=234ms    p(90)=80ms   p(95)=120ms
http_req_sending...............: avg=12.34ms  min=1ms      med=10ms     max=156ms    p(90)=20ms   p(95)=30ms
http_req_tls_handshaking.......: avg=0s       min=0s       med=0s       max=0s       p(90)=0s     p(95)=0s
http_req_waiting...............: avg=2.44s    min=89ms     med=2.05s    max=8.7s     p(90)=4.1s   p(95)=4.7s
http_reqs......................: 124801 165.3/s
iteration_duration.............: avg=6.05s    min=1.2s     med=5.8s     max=15.3s    p(90)=8.5s   p(95)=10.2s
iterations.....................: 124801 165.3/s
vus............................: 1000   min=0         max=1000
vus_max........................: 1000   min=1000      max=1000
```

### Success Criteria

✅ **PASS** if:
- `http_req_duration p(95)` < 5000ms (5 seconds)
- `http_req_failed` < 1% (0.01 rate)
- `http_reqs` > 100 req/s

❌ **FAIL** if any threshold is exceeded

### Custom Metrics

Operation-specific metrics are also reported:

- `create_task_duration`: Latency for task creation
- `list_tasks_duration`: Latency for listing tasks
- `update_task_duration`: Latency for updating tasks
- `delete_task_duration`: Latency for deleting tasks
- `create_task_errors`: Error rate for task creation
- `list_tasks_errors`: Error rate for listing tasks
- `update_task_errors`: Error rate for updating tasks
- `delete_task_errors`: Error rate for deleting tasks

## Troubleshooting

### Backend Not Accessible

**Error**: `Backend health check failed!`

**Solution**:
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check Docker containers: `docker ps`
3. Review backend logs: `docker logs <backend-container>`
4. Ensure database is accessible

### High Error Rates

**Symptom**: `http_req_failed > 1%`

**Possible Causes**:
1. Database connection pool exhausted
2. Rate limiting enabled
3. Insufficient backend resources (CPU/memory)
4. Network issues

**Solutions**:
- Increase database connection pool size in `backend/app/core/config.py`
- Scale backend horizontally: `kubectl scale deployment todo-backend --replicas=3`
- Review Kubernetes resource limits in `values.yaml`
- Monitor database performance with Grafana dashboards

### High Latency

**Symptom**: `http_req_duration p(95) > 5000ms`

**Possible Causes**:
1. Database query performance issues
2. Backend CPU/memory constraints
3. Network bottlenecks
4. Dapr sidecar overhead

**Solutions**:
- Add database indexes on frequently queried fields
- Optimize slow queries (review PostgreSQL logs)
- Increase backend resource limits
- Enable database connection pooling
- Cache frequently accessed data with Redis

### Connection Timeouts

**Error**: `connection timeout` or `socket hang up`

**Solutions**:
1. Increase timeout in k6 script:
   ```javascript
   export const options = {
     timeout: '60s', // Increase timeout
   };
   ```
2. Check network connectivity
3. Verify application is not overwhelmed (check resource usage)

## CI/CD Integration

### GitHub Actions

Add load testing to your CI/CD pipeline:

```yaml
# .github/workflows/load-test.yml
name: Load Test

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 2 * * *' # Daily at 2 AM

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install k6
        run: |
          sudo gpg -k
          sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6

      - name: Run load test
        env:
          BASE_URL: ${{ secrets.PRODUCTION_URL }}
        run: |
          k6 run --out json=results.json load-test/load-test.js

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: load-test-results
          path: results.json
```

## Advanced Testing

### Spike Testing

Test system resilience to sudden traffic spikes:

```bash
k6 run --vus 2000 --duration 1m load-test.js
```

### Stress Testing

Push system beyond normal capacity:

```bash
k6 run --vus 5000 --duration 10m load-test.js
```

### Soak Testing

Long-duration test for memory leaks:

```bash
k6 run --vus 500 --duration 2h load-test.js
```

## Results Directory Structure

```
load-test/
├── README.md                    # This file
├── load-test.js                 # Main k6 test script
├── results/                     # Test results (gitignored)
│   ├── load-test-results.json   # JSON output
│   ├── load-test-report.html    # HTML report
│   └── metrics.txt              # Summary metrics
└── docker-compose-monitoring.yml # InfluxDB + Grafana (optional)
```

## References

- [k6 Documentation](https://k6.io/docs/)
- [k6 Performance Testing Best Practices](https://k6.io/docs/testing-guides/performance-testing/)
- [k6 Examples](https://github.com/grafana/k6-learn)
- [Load Testing with k6](https://www.youtube.com/watch?v=r-Jte8Y8zag)

## Support

For issues or questions:

1. Check backend logs: `kubectl logs -l app.kubernetes.io/name=todo-app`
2. Review k6 documentation: https://k6.io/docs/
3. Monitor application metrics in Grafana dashboards
4. Contact development team with results JSON file
