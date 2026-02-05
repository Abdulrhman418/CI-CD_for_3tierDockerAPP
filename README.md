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

This project demonstrates how to deploy a **3-tier application** on **AWS ECS Fargate** using **Service Connect**.  
It consists of two main services:

- **API Service** – Handles backend logic and database interactions.
- **Web Service** – Serves the frontend and communicates with the API.

The setup ensures secure communication between services via ECS Service Connect, proper logging, and scalable deployment.

---

## Prerequisites

Before deploying, ensure the following are in place:

- AWS CLI configured with appropriate credentials.
- Docker installed for building container images.
- AWS VPC with subnets (public/private) and security groups.
- IAM roles with necessary permissions for ECS tasks and execution.

**Required IAM Roles:**

1. **Task Role** – For container access to AWS resources (Secrets Manager, S3, etc.).
2. **Execution Role** – For ECS agent to pull container images and send logs to CloudWatch.

Other prerequisites:

- CloudWatch log groups for API and Web services.
- ECR repositories for storing Docker images.

---

## Architecture

       ┌────────────┐
       │   Web UI   │
       └─────┬──────┘
             │
      HTTP  │
             ▼
       ┌────────────┐
       │   API      │
       │  Service   │
       └─────┬──────┘
             │
        Database / Other Services

- **Web Service** communicates with **API Service** using Service Connect DNS (`api`).
- Both services run on **Fargate** with `awsvpc` networking mode.
- Service Connect ensures secure service-to-service communication within the same VPC.

---

## Deployment Steps

### 1. Build and Push Docker Images

- Build Docker images for API and Web services.
- Push images to **Amazon ECR**.

### 2. Create ECS Cluster

- Create a cluster named `3tierapp`.

### 3. Set Up IAM Roles

- Create Task Roles for API and Web.
- Create Execution Role and attach `AmazonECSTaskExecutionRolePolicy`.

### 4. Configure Network

- Create security groups:
  - **API SG** allows inbound traffic from Web SG on port 5000.
  - **Web SG** allows outbound traffic to API and internet.
- Ensure subnets are available and configure NAT Gateway if using private subnets.

### 5. Create CloudWatch Log Groups

- `/ecs/api-tier` for API logs.
- `/ecs/web-tier` for Web logs.

### 6. Register Task Definitions

- Define containers, port mappings, environment variables, CPU, memory, logging, and Service Connect configuration.
- Register API and Web task definitions in ECS.

### 7. Service Discovery

- Create a **Private DNS Namespace** for Service Connect.
- Both services must use the same namespace to communicate.

### 8. Create ECS Services

- **API Service**: `Client + Server` Service Connect mode.
- **Web Service**: `Client only` mode.
- Enable ECS Exec and configure deployment settings.

### 9. Verify Deployment

- List services in ECS cluster:

  ```bash
  aws ecs list-services --cluster 3tierapp

Verify Services Health and Status

Use this command to check the health and status of your services:

aws ecs describe-services --cluster 3tierapp --services api-service web-service

Test Service Connect DNS from Inside Web Container

Open an interactive shell inside the Web container:

aws ecs execute-command \
  --cluster 3tierapp \
  --task <WEB_TASK_ID> \
  --container web-tair \
  --interactive \
  --command "/bin/sh"


Inside the container, test connectivity to the API service:

# Ping the API service
ping api

# Test HTTP endpoint
curl http://api:5000/products
