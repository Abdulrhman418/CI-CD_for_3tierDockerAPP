# 3-Tier Docker Application

## Overview
This is a simple **3-tier application** that demonstrates:

- Dockerfile image builds  
- Multi-container setup using **docker-compose**  
- Deployment using **Docker Swarm**  
- Isolation using **networks, volumes & secrets**  

## Architecture
**Services:**
- **Web** (Flask) → renders product list
- **API** (Flask) → retrieves products from DB
- **Database** (MySQL) → stores product data

**Flow:**  
➡️ Browser → Web → API → DB

## .env (Docker Compose)
A `.env` file is used to store environment variables locally (not for Swarm):

```
DB_PASSWORD=root123
```

Example usage inside `docker-compose.yml`:

## Isolation & Security
- **Networks:**
  - `mynet-app` → Web + API
  - `mynet-back` → API + DB

- **Volumes:**
  - Persistent MySQL storage

- **Secrets (Swarm):**
  - `docker secret create db_password -`

## Run with Docker Compose
```bash
docker-compose up -d
```

Access:
- Web → http://localhost:8080
- API → http://localhost:5000/products

## Database Init
```bash
docker exec -it mydb sh
mysql -u root -p
```

SQL Example:
```sql
CREATE TABLE products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  price DECIMAL(10,2)
);

INSERT INTO products (name, price) VALUES
("Laptop", 900),
("Phone", 450),
("Keyboard", 30);
```

## Testing
API:
```bash
curl http://localhost:5000/products
```

Web:
Open browser:
```
http://localhost:8080
```

Container communication:
```bash
docker exec -it web sh
wget -qO- http://api:5000/products
```

## Swarm Deployment
```bash
docker swarm init
echo "root123" | docker secret create db_password -
docker stack deploy -c docker-stack.yml myapp
```

---
⭐ The goal of this project is to learn **Docker networking, persistence, secrets, and orchestration**.




# 3-Tier ECS Fargate Deployment

## Overview

This guide explains step-by-step how to deploy a **3-tier application** on **AWS ECS Fargate** using **Service Connect**. It covers **initial setup**, **task and service definition preparation**, and **deployment steps** with AWS CLI commands.

The application consists of two main services:

- **API Service** – Backend service handling business logic.
- **Web Service** – Frontend service communicating with the API.

All communication between services uses **Service Connect**, and proper logging is configured with **CloudWatch**.

> **Note:** For this test application, the database password is passed as an environment variable directly in the task definition. In **production**, it is recommended to use **Secrets Manager** and reference secrets in the task definition for security. The simple test application used here does not handle the JSON format response returned by Secrets Manager, which prevents proper splitting and parsing, so using secrets was skipped to avoid redoing the image build and redeploying everything from scratch.

---

## Step 1: Initial Setup (SG, Log Groups, ECR, IAM Roles)

### 1.1 Create Security Groups

- **API Security Group** allows inbound from Web SG on port 5000.
- **Web Security Group** allows outbound traffic to API and internet.

```bash
aws ec2 create-security-group --group-name ecs-api-sg --description "API SG" --vpc-id <vpc-id>
aws ec2 create-security-group --group-name ecs-web-sg --description "Web SG" --vpc-id <vpc-id>
```

### 1.2 Create CloudWatch Log Groups

```bash
aws logs create-log-group --log-group-name /ecs/api-tier
aws logs create-log-group --log-group-name /ecs/web-tier
```

### 1.3 Push Docker Images to ECR

Create repositories:

```bash
aws ecr create-repository --repository-name api-tier
aws ecr create-repository --repository-name web-tier
```

Build and push images:

```bash
# API image
docker build -t api-tier ./api
docker tag api-tier:latest <account-id>.dkr.ecr.<region>.amazonaws.com/api-tier:latest
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/api-tier:latest

# Web image
docker build -t web-tier ./web
docker tag web-tier:latest <account-id>.dkr.ecr.<region>.amazonaws.com/web-tier:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/web-tier:latest
```

### 1.4 Create IAM Roles and Attach Policies

**Execution Role** (ecsTaskExecutionRole) must have the following AWS managed policies:

| Policy Name | Type | Attached Entities |
|-------------|------|-----------------|
| AmazonECSTaskExecutionRolePolicy | AWS managed | 1 |
| CloudWatchLogsFullAccess | AWS managed | 1 |
| SecretsManagerReadWrite | AWS managed | 1 |

> **Reason:** Execution role needs permission to pull container images from ECR, send logs to CloudWatch, and read/write secrets if needed.

**Web Task Role** (`webTaskRole`) must have:

| Policy Name | Type | Attached Entities |
|-------------|------|-----------------|
| AmazonSSMManagedInstanceCore | AWS managed | 1 |

> **Reason:** Needed to enable ECS Exec for debugging and interactive shell access inside the container.

**API Task Role** (`apiTaskRole`) must have:

| Policy Name | Type | Attached Entities |
|-------------|------|-----------------|
| AmazonSSMManagedInstanceCore | AWS managed | 2 |
| SecretsManagerReadWrite | AWS managed | 1 |

> **Reason:** API service needs to retrieve database password from Secrets Manager and optionally use ECS Exec for debugging.

```bash
aws iam create-role --role-name apiTaskRole --assume-role-policy-document file://trust-policy.json
aws iam create-role --role-name webTaskRole --assume-role-policy-document file://trust-policy.json
aws iam create-role --role-name ecsTaskExecutionRole --assume-role-policy-document file://ecs-trust-policy.json
aws iam attach-role-policy --role-name ecsTaskExecutionRole --policy-arn arn:aws:iam::aws:policy/AmazonECSTaskExecutionRolePolicy
aws iam attach-role-policy --role-name ecsTaskExecutionRole --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess
aws iam attach-role-policy --role-name ecsTaskExecutionRole --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite
aws iam attach-role-policy --role-name webTaskRole --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
aws iam attach-role-policy --role-name apiTaskRole --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
aws iam attach-role-policy --role-name apiTaskRole --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite
```

---

## Step 2: Prepare Task and Service Definition Files

- Create **Task Definition JSON files** for API and Web, specifying:
  - Container image and name
  - Port mappings
  - Environment variables (**DB password is set directly here for testing**)
  - CPU and memory
  - Logging configuration
  - Service Connect configuration (API as Client + Server, Web as Client only)

- Create **Service JSON files** for API and Web, specifying:
  - Cluster: **`3tierapp`** (important: cluster name in ECS service file must match)
  - Network configuration: subnets, security groups, assignPublicIp
  - Enable ECS Exec
  - Deployment configuration (min 50%, max 200%)
  - Service Connect configuration

- Create **Private DNS Namespace** for Service Connect:

```bash
aws servicediscovery create-private-dns-namespace \
  --name 3tierapp \
  --vpc <vpc-id> \
  --description "Private namespace for ECS Service Connect"
```

> **Important:** When using these files, replace all placeholder values like ARN, account IDs, and VPC IDs with the actual resources you created.

---

## Step 3: Deploy Using AWS CLI Commands

### 3.1 Create ECS Cluster

```bash
aws ecs create-cluster --cluster-name 3tierapp
```

> **Note:** Cluster name must match `cluster` field in your service JSON files.

### 3.2 Register Task Definitions

```bash
aws ecs register-task-definition --cli-input-json file://api-task.json
aws ecs register-task-definition --cli-input-json file://web-task.json
```

### 3.3 Create Services

```bash
aws ecs create-service --cli-input-json file://api-server.json
aws ecs create-service --cli-input-json file://web-server.json
```

### 3.4 Verify Deployment

#### List Services

```bash
aws ecs list-services --cluster 3tierapp
```

#### Check Health and Status

```bash
aws ecs describe-services --cluster 3tierapp --services api-service web-service
```

#### Test Service Connect DNS from Web Container

```bash
aws ecs execute-command \
  --cluster 3tierapp \
  --task <WEB_TASK_ID> \
  --container web-tair \
  --interactive \
  --command "/bin/sh"
```

Inside the container:

```bash
ping api
curl http://api:5000/products
```

---

## Important Notes

- Assign public IP only if using public subnets.
- Ensure NAT Gateway exists if using private subnets.
- Both services must use the same VPC and Service Connect namespace.
- In testing, DB password is passed as environment variable. In production, use Secrets Manager.
- ECS Execution roles and Task roles must have correct policies attached as described above.
- Replace all placeholder values in JSON files (ARNs, account IDs, VPC IDs, secret names) with the actual values created in your AWS account.
- The simple test application cannot handle JSON secrets; hence we skipped secret splitting to avoid rebuilding images.
- Monitor logs in CloudWatch for troubleshooting.

---

## References

- [AWS ECS Fargate Documentation](https://docs.aws.amazon.com/ecs/latest/developerguide/what-is-fargate.html)  
- [AWS Service Connect Guide](https://docs.aws.amazon.com/AmazonECS/latest/userguide/service-connect.html)  
- [ECR Docker Image Push Guide](https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-push-ecr-image.html)

