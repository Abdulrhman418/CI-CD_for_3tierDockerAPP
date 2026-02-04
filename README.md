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



