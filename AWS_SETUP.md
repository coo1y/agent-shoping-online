# AWS Setup Guide for Agent Shopping Online

This guide explains how to set up AWS infrastructure for deploying this application.

## Architecture Overview

- **Frontend**: Next.js app deployed to AWS ECS Fargate
- **Backend**: FastAPI app deployed to AWS ECS Fargate
- **Database**: AWS RDS PostgreSQL
- **Container Registry**: AWS ECR
- **Load Balancer**: AWS Application Load Balancer (ALB)

## Prerequisites

1. AWS Account with appropriate permissions
2. AWS CLI installed and configured
3. Docker installed locally (for testing)

## Step 1: Create ECR Repositories

```bash
# Create ECR repositories for frontend and backend
aws ecr create-repository --repository-name agent-shop-frontend --region ap-southeast-1
aws ecr create-repository --repository-name agent-shop-backend --region ap-southeast-1
```

## Step 2: Create ECS Cluster

```bash
aws ecs create-cluster --cluster-name agent-shop-cluster --region ap-southeast-1
```

## Step 3: Create RDS PostgreSQL Database

```bash
aws rds create-db-instance \
  --db-instance-identifier agent-shop-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15 \
  --master-username admin \
  --master-user-password <YOUR_SECURE_PASSWORD> \
  --allocated-storage 20 \
  --vpc-security-group-ids <YOUR_SECURITY_GROUP_ID> \
  --db-name techshop \
  --region ap-southeast-1
```

## Step 4: Create Task Definitions

### Backend Task Definition (`task-definition-backend.json`)

```json
{
  "family": "agent-shop-backend-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::<ACCOUNT_ID>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<ACCOUNT_ID>.dkr.ecr.ap-southeast-1.amazonaws.com/agent-shop-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://admin:<PASSWORD>@<RDS_ENDPOINT>:5432/techshop"
        },
        {
          "name": "OPENAI_API_KEY",
          "value": "<YOUR_OPENAI_API_KEY>"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/agent-shop-backend",
          "awslogs-region": "ap-southeast-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Frontend Task Definition (`task-definition-frontend.json`)

```json
{
  "family": "agent-shop-frontend-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::<ACCOUNT_ID>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "frontend",
      "image": "<ACCOUNT_ID>.dkr.ecr.ap-southeast-1.amazonaws.com/agent-shop-frontend:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "NEXT_PUBLIC_API_URL",
          "value": "https://api.yourdomain.com"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/agent-shop-frontend",
          "awslogs-region": "ap-southeast-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Register the task definitions:

```bash
aws ecs register-task-definition --cli-input-json file://task-definition-backend.json
aws ecs register-task-definition --cli-input-json file://task-definition-frontend.json
```

## Step 5: Create ECS Services

```bash
# Create backend service
aws ecs create-service \
  --cluster agent-shop-cluster \
  --service-name agent-shop-backend-service \
  --task-definition agent-shop-backend-task \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[<SUBNET_ID>],securityGroups=[<SECURITY_GROUP_ID>],assignPublicIp=ENABLED}"

# Create frontend service
aws ecs create-service \
  --cluster agent-shop-cluster \
  --service-name agent-shop-frontend-service \
  --task-definition agent-shop-frontend-task \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[<SUBNET_ID>],securityGroups=[<SECURITY_GROUP_ID>],assignPublicIp=ENABLED}"
```

## Step 6: Configure GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

| Secret Name | Description |
|-------------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS IAM user access key ID |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM user secret access key |

### Required IAM Permissions

Create an IAM user with the following policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecs:DescribeServices",
        "ecs:DescribeTaskDefinition",
        "ecs:DescribeTasks",
        "ecs:ListTasks",
        "ecs:RegisterTaskDefinition",
        "ecs:UpdateService"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": "*",
      "Condition": {
        "StringLike": {
          "iam:PassedToService": "ecs-tasks.amazonaws.com"
        }
      }
    }
  ]
}
```

## Step 7: Configure Environment Variables

### Backend Environment Variables

Set these in your ECS task definition or AWS Secrets Manager:

- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for the AI agent

### Frontend Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API URL

## Workflow Files

The CI/CD pipeline consists of two workflow files:

1. **`.github/workflows/ci.yml`**: Runs on all pushes and PRs
   - Lints frontend (ESLint)
   - Builds frontend
   - Lints backend (Ruff)

2. **`.github/workflows/deploy-aws.yml`**: Runs on pushes to `main`
   - Builds and pushes Docker images to ECR
   - Deploys to ECS Fargate

## Customization

### Change AWS Region

Update the `AWS_REGION` environment variable in `.github/workflows/deploy-aws.yml`:

```yaml
env:
  AWS_REGION: your-preferred-region
```

### Change Resource Names

Update the resource names in the workflow file to match your AWS setup:

```yaml
env:
  ECR_REPOSITORY_FRONTEND: your-frontend-repo
  ECR_REPOSITORY_BACKEND: your-backend-repo
  ECS_CLUSTER: your-cluster-name
  ECS_SERVICE_FRONTEND: your-frontend-service
  ECS_SERVICE_BACKEND: your-backend-service
```

## Local Testing

Test Docker builds locally before pushing:

```bash
# Build and test backend
cd backend
docker build -t agent-shop-backend .
docker run -p 8000:8000 agent-shop-backend

# Build and test frontend
cd ..
docker build -t agent-shop-frontend .
docker run -p 3000:3000 agent-shop-frontend
```

## Troubleshooting

### Common Issues

1. **ECR Login Failed**: Ensure AWS credentials have ECR permissions
2. **Task Definition Not Found**: Register task definitions before first deployment
3. **Service Stability Timeout**: Check CloudWatch logs for container errors
4. **Database Connection Failed**: Verify security group allows ECS to connect to RDS

### View Logs

```bash
# View ECS service logs
aws logs tail /ecs/agent-shop-backend --follow
aws logs tail /ecs/agent-shop-frontend --follow
```
