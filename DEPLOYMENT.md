# Deployment Guide

## Local Development

### Prerequisites
- Python 3.10+
- 4GB RAM minimum
- 500MB disk space
- Ollama local model

### Setup

```bash
# 1. Clone/Extract project
cd insurance_analytics

# 2. Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
# or
source venv/bin/activate      # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Edit .env with your Ollama local model

# 5. Initialize
python initialize.py

# 6. Run
python main.py
```

## Running Components

### Full Pipeline
```bash
python main.py
```
Runs all 8 stages sequentially. Output in `data/outputs/`.

### Dashboard Only
```bash
streamlit run src/dashboard/app.py
```
Access at `http://localhost:8501`

### Individual Scripts
```bash
# Show examples
python examples/pipeline_example.py
```

## Cloud Deployment

### Docker Deployment

**Dockerfile**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV LOCAL_LLM_MODEL=${LOCAL_LLM_MODEL}

CMD ["python", "main.py"]
```

**Build and Run**:
```bash
docker build -t insurance-analytics .
docker run -e LOCAL_LLM_MODEL=mistral insurance-analytics
```

### Docker Compose (with dashboard)

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  analytics:
    build: .
    environment:
      LOCAL_LLM_MODEL: ${LOCAL_LLM_MODEL}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    
  dashboard:
    build: .
    command: streamlit run src/dashboard/app.py
    ports:
      - "8501:8501"
    environment:
      LOCAL_LLM_MODEL: ${LOCAL_LLM_MODEL}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
```

**Run**:
```bash
docker-compose up
```

### AWS Deployment

**EC2 Setup**:
```bash
# 1. Launch Ubuntu instance (t3.medium or larger)
# 2. SSH into instance
ssh -i key.pem ec2-user@instance-ip

# 3. Install Python and dependencies
sudo apt-get update
sudo apt-get install python3.10 python3-pip git

# 4. Clone project
git clone <repo-url>
cd insurance_analytics

# 5. Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Configure
ollama serve

# 7. Run
python main.py
```

**Using AWS Lambda** (for dashboard):
1. Package as ZIP
2. Upload to Lambda
3. Set handler to Streamlit integration
4. Configure API Gateway

### GCP Deployment

**Cloud Run Setup**:
```bash
# Build and deploy dashboard
gcloud run deploy insurance-analytics \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars LOCAL_LLM_MODEL=mistral,LOCAL_LLM_HOST=http://localhost:11434
```

### Azure Deployment

**Container Instances**:
```bash
az container create \
  --resource-group mygroup \
  --name insurance-analytics \
  --image insurance-analytics:latest \
  --environment-variables LOCAL_LLM_MODEL=mistral \
  --ports 8501
```

## Monitoring & Logging

### Local Logs
```bash
tail -f logs/app.log
```

### Cloud Logging

**AWS CloudWatch**:
```python
import boto3
logs = boto3.client('logs')
logs.put_log_events(
    logGroupName='/insurance-analytics',
    logStreamName='pipeline',
    logEvents=[...]
)
```

**GCP Logging**:
```python
from google.cloud import logging as cloud_logging
client = cloud_logging.Client()
client.logger('insurance-analytics').log_struct({...})
```

## Performance Optimization

### Batch Processing
```python
# Process multiple companies in parallel
from multiprocessing import Pool

companies = list(COMPANIES.keys())
with Pool(4) as p:
    results = p.map(process_company, companies)
```

### Caching
```python
import redis

redis_client = redis.Redis()
# Cache embedding results
redis_client.set(f"embedding:{text_hash}", embedding, ex=86400)
```

### Database Optimization
```python
# Index frequently searched fields
vector_db.create_index('company')
vector_db.create_index('source_type')
```

## Security

### Local Model Management
```bash
# Use AWS Secrets Manager
ollama pull mistral

# Or environment variables
export LOCAL_LLM_MODEL=mistral
```

### Data Privacy
- Store data locally or in private cloud
- Encrypt data at rest
- Use VPN for data transfer
- Regular backups

### Access Control
```python
# Add authentication (future)
from fastapi_auth import api_key_header

@app.get("/api/report")
async def get_report(api_key: str = Depends(api_key_header)):
    # Validate key
    # Return report
```

## Maintenance

### Regular Updates
```bash
# Update dependencies monthly
pip install --upgrade -r requirements.txt

# Monitor logs weekly
tail -f logs/app.log | grep ERROR

# Run tests
python -m pytest tests/
```

### Data Cleanup
```bash
# Archive old data
find data/raw -mtime +30 -exec tar -czf archive-{}.tar.gz {} \;

# Clear cache
rm -rf data/embeddings/*
```

### Backup Strategy
```bash
# Daily backup
tar -czf backup-$(date +%Y%m%d).tar.gz data/ logs/

# Upload to cloud
aws s3 cp backup-*.tar.gz s3://backups/insurance-analytics/
```

## Scaling

### Horizontal Scaling
```python
# Run multiple pipeline instances
# Use load balancer to distribute
# Share data via cloud storage
```

### Vertical Scaling
```python
# Increase instance size
# Optimize batch sizes
# Reduce chunk overlap
```

### Database Scaling
```python
# Distributed vector DB
# Federated search
# Replica management
```

## Troubleshooting

### High Memory Usage
```python
# Reduce batch sizes
EMBEDDING_BATCH_SIZE = 10  # from 100

# Stream processing
def stream_documents(docs):
    for doc in docs:
        yield process_document(doc)
```

### Slow Embeddings
```python
# Use cache
# Batch requests
# Parallel processing
```

### API Rate Limits
```python
# Implement backoff
import tenacity

@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential()
)
def call_local_llm():
    pass
```

## Monitoring Dashboard

### Metrics to Track
- Pipeline execution time
- Document count
- Embedding success rate
- API call count
- Error rate
- Storage usage

### Alerts
```python
# Send alerts on failures
from slack_sdk import WebClient

slack_client = WebClient(token=SLACK_TOKEN)

def send_alert(message):
    slack_client.chat_postMessage(
        channel='#analytics-alerts',
        text=f":warning: {message}"
    )
```

## Cost Optimization

### Local LLM
- Use all-MiniLM-L6-v2 for fast local embeddings
- Batch requests
- Cache results
- Monitor usage

### Cloud Infrastructure
- Use spot instances
- Auto-scaling groups
- Scheduled shutdown during off-peak
- Reserved instances

### Storage
- Archive old data
- Compress outputs
- Use cheaper storage classes
- Regular cleanup

## Documentation

Update documentation after deployment:
```bash
# Document configuration
echo "## Deployment Config" >> DEPLOYMENT.md

# Document URLs
echo "Dashboard: https://analytics.example.com" >> DEPLOYMENT.md

# Document credentials (securely)
# Store in secure credential manager, not in git
```

---

**For production deployment, consider**:
- Load testing before launch
- Disaster recovery plan
- 24/7 monitoring
- On-call support
- Regular security audits

