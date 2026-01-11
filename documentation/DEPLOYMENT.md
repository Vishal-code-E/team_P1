# Deployment Guide

This guide covers deploying the AI Knowledge Base + Chatbot to various platforms.

## Table of Contents

- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
  - [AWS](#aws-deployment)
  - [Google Cloud Platform](#gcp-deployment)
  - [Azure](#azure-deployment)
  - [Heroku](#heroku-deployment)

## Local Development

### Quick Start

**Linux/Mac:**
```bash
./start.sh
```

**Windows:**
```
start.bat
```

### Manual Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run the application:
```bash
python main.py
```

## Docker Deployment

### Using Docker Compose (Recommended)

1. Configure your `.env` file with API keys

2. Build and run:
```bash
docker-compose up -d
```

3. View logs:
```bash
docker-compose logs -f
```

4. Stop the service:
```bash
docker-compose down
```

### Using Docker Directly

1. Build the image:
```bash
docker build -t ai-knowledge-base .
```

2. Run the container:
```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/uploads:/app/uploads \
  -e OPENAI_API_KEY=your_key_here \
  --name ai-kb \
  ai-knowledge-base
```

## Cloud Deployment

### AWS Deployment

#### Option 1: AWS EC2

1. Launch an EC2 instance (t3.medium or larger recommended)
2. SSH into the instance
3. Install Docker:
```bash
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user
```

4. Clone and deploy:
```bash
git clone https://github.com/Vishal-code-E/team_P1.git
cd team_P1
cp .env.example .env
# Edit .env with your keys
docker-compose up -d
```

5. Configure security group to allow port 8000

#### Option 2: AWS ECS (Fargate)

1. Create ECR repository:
```bash
aws ecr create-repository --repository-name ai-knowledge-base
```

2. Build and push image:
```bash
docker build -t ai-knowledge-base .
docker tag ai-knowledge-base:latest {account}.dkr.ecr.{region}.amazonaws.com/ai-knowledge-base:latest
docker push {account}.dkr.ecr.{region}.amazonaws.com/ai-knowledge-base:latest
```

3. Create ECS task definition with:
   - Container port: 8000
   - Environment variables from `.env`
   - EFS volume for `/app/data`

4. Create ECS service with ALB

### GCP Deployment

#### Using Cloud Run

1. Build and push to GCR:
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-knowledge-base
```

2. Deploy to Cloud Run:
```bash
gcloud run deploy ai-knowledge-base \
  --image gcr.io/PROJECT_ID/ai-knowledge-base \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your_key_here
```

3. Mount Cloud Storage for persistent data:
```bash
gcloud run services update ai-knowledge-base \
  --execution-environment gen2 \
  --add-volume name=data,type=cloud-storage,bucket=your-bucket \
  --add-volume-mount volume=data,mount-path=/app/data
```

### Azure Deployment

#### Using Azure Container Instances

1. Create resource group:
```bash
az group create --name ai-kb-rg --location eastus
```

2. Create container instance:
```bash
az container create \
  --resource-group ai-kb-rg \
  --name ai-knowledge-base \
  --image your-registry/ai-knowledge-base:latest \
  --dns-name-label ai-kb-unique \
  --ports 8000 \
  --environment-variables OPENAI_API_KEY=your_key_here
```

### Heroku Deployment

1. Create `Procfile`:
```
web: python main.py
```

2. Deploy:
```bash
heroku create ai-knowledge-base
heroku config:set OPENAI_API_KEY=your_key_here
git push heroku main
```

## Environment Variables

Set these environment variables in your deployment:

### Required
- `OPENAI_API_KEY`: Your OpenAI API key

### Optional
- `CONFLUENCE_URL`: Confluence instance URL
- `CONFLUENCE_USERNAME`: Confluence username
- `CONFLUENCE_API_TOKEN`: Confluence API token
- `SLACK_BOT_TOKEN`: Slack bot token
- `SLACK_APP_TOKEN`: Slack app token
- `APP_HOST`: Host to bind to (default: 0.0.0.0)
- `APP_PORT`: Port to bind to (default: 8000)
- `EMBEDDING_MODEL`: OpenAI embedding model (default: text-embedding-3-small)
- `LLM_MODEL`: OpenAI LLM model (default: gpt-4-turbo-preview)

## Persistent Storage

The application stores data in these directories:
- `data/chroma`: Vector database
- `uploads`: Uploaded PDF files

Ensure these directories are persisted using:
- Docker volumes
- EFS/Cloud Storage/Azure Files for cloud deployments

## Scaling Considerations

### Horizontal Scaling

The application is stateless except for the vector database. To scale horizontally:

1. Use a shared vector database (e.g., Pinecone, Weaviate, or Qdrant)
2. Store uploaded files in object storage (S3, GCS, Azure Blob)
3. Run multiple instances behind a load balancer

### Vertical Scaling

For single-instance deployments:
- **Minimum**: 2 CPU, 4GB RAM
- **Recommended**: 4 CPU, 8GB RAM
- **Large deployments**: 8+ CPU, 16GB+ RAM

## Monitoring

### Health Checks

The application provides a health endpoint:
```
GET /health
```

Use this for load balancer health checks.

### Logs

Application logs are written to stdout. Configure log aggregation:
- CloudWatch (AWS)
- Cloud Logging (GCP)
- Application Insights (Azure)

### Metrics

Monitor these metrics:
- Response time
- Request rate
- Error rate
- Memory usage
- Vector database size

## Security

### Best Practices

1. **Never commit `.env` files**
2. **Use secrets management**:
   - AWS Secrets Manager
   - GCP Secret Manager
   - Azure Key Vault
   - HashiCorp Vault

3. **Enable HTTPS**: Use a reverse proxy (nginx) or cloud load balancer
4. **API Rate Limiting**: Implement rate limiting for production
5. **Authentication**: Add authentication for production use
6. **Network Security**: Use VPC/private networks for cloud deployments

### Adding Authentication

To add basic authentication, modify `src/api/routes.py`:

```python
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "secret")
    return correct_username and correct_password

@app.post("/api/query")
async def query_knowledge_base(
    request: QueryRequest,
    credentials: HTTPBasicCredentials = Depends(security)
):
    if not verify_credentials(credentials):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # ... rest of the function
```

## Troubleshooting

### Port Already in Use

Change the port in `.env`:
```
APP_PORT=8080
```

### Out of Memory

Increase container memory limits or reduce chunk size in `.env`:
```
CHUNK_SIZE=500
```

### Slow Queries

1. Reduce the number of retrieved documents
2. Use a faster embedding model
3. Add more CPU/RAM to your deployment

## Support

For deployment issues, please open an issue on GitHub.
