# Deployment Guide

## Local Development (Docker Compose)

### Setup
```bash
# 1. Clone repository
git clone <repo-url>
cd roommate-match-app

# 2. Copy environment files
cp .env.example apps/api/.env
cp apps/web/.env.local.example apps/web/.env.local

# 3. Start services
docker-compose up -d

# 4. Run migrations
docker-compose exec api alembic upgrade head

# 5. Seed database
docker-compose exec api python scripts/seed.py

# 6. Access application
# Web: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Development Workflow
```bash
# View logs
docker-compose logs -f

# Restart a service
docker-compose restart api

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up --build
```

## Production Deployment

### Option 1: Vercel (Frontend) + Render (Backend) + Managed Postgres

#### Database Setup (Render/Neon/Supabase)
1. Create PostgreSQL database
2. Note connection string
3. Add to environment variables

#### Backend Deployment (Render)
1. Create new Web Service on Render
2. Connect GitHub repository
3. Settings:
   - **Build Command**: `cd apps/api && pip install -r requirements.txt`
   - **Start Command**: `cd apps/api && alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.11
4. Environment Variables:
   ```
   DATABASE_URL=<postgres-connection-string>
   SECRET_KEY=<generate-random-secret>
   ALLOWED_ORIGINS=https://your-domain.vercel.app
   ENVIRONMENT=production
   ```
5. Deploy

#### Frontend Deployment (Vercel)
1. Install Vercel CLI: `npm i -g vercel`
2. From project root:
   ```bash
   cd apps/web
   vercel
   ```
3. Environment Variables in Vercel Dashboard:
   ```
   NEXT_PUBLIC_API_URL=https://your-api.onrender.com
   NEXTAUTH_URL=https://your-domain.vercel.app
   NEXTAUTH_SECRET=<generate-random-secret>
   ```
4. Redeploy if needed

### Option 2: Single-Host Docker Deployment (VPS)

#### Prerequisites
- Ubuntu 22.04 VPS
- Docker & Docker Compose installed
- Domain name pointed to server

#### Setup
```bash
# 1. SSH into server
ssh user@your-server.com

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 3. Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Clone repository
git clone <repo-url>
cd roommate-match-app

# 5. Create production env files
nano apps/api/.env
nano apps/web/.env.local

# 6. Start with production compose
docker-compose -f docker-compose.prod.yml up -d

# 7. Run migrations
docker-compose exec api alembic upgrade head

# 8. Create admin user
docker-compose exec api python scripts/create_admin.py
```

#### Production docker-compose.prod.yml
```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: leasepeace
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: leasepeace
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  api:
    build: ./apps/api
    environment:
      DATABASE_URL: postgresql://leasepeace:${DB_PASSWORD}@db:5432/leasepeace
      SECRET_KEY: ${API_SECRET_KEY}
      ALLOWED_ORIGINS: https://yourdomain.com
      ENVIRONMENT: production
    depends_on:
      - db
    restart: always

  web:
    build: ./apps/web
    environment:
      NEXT_PUBLIC_API_URL: https://api.yourdomain.com
      NEXTAUTH_URL: https://yourdomain.com
      NEXTAUTH_SECRET: ${NEXTAUTH_SECRET}
    depends_on:
      - api
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    depends_on:
      - web
      - api
    restart: always

volumes:
  postgres_data:
```

#### Nginx Configuration
```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    upstream web {
        server web:3000;
    }

    server {
        listen 80;
        server_name yourdomain.com;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 301 https://$host$request_uri;
        }
    }

    server {
        listen 443 ssl;
        server_name yourdomain.com;

        ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

        location /api {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location / {
            proxy_pass http://web;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

#### SSL Setup with Let's Encrypt
```bash
# Install certbot
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --webroot -w /var/www/certbot \
  -d yourdomain.com \
  -d api.yourdomain.com

# Auto-renewal cron
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### Post-Deployment Checklist

- [ ] Database migrations applied
- [ ] Admin user created
- [ ] Environment variables set
- [ ] SSL certificates installed
- [ ] Backups configured
- [ ] Monitoring set up (Sentry, Datadog, etc.)
- [ ] Rate limiting enabled
- [ ] Email service configured (SendGrid, Postmark)
- [ ] Payment processing configured (Stripe)
- [ ] Domain DNS configured
- [ ] Firewall rules configured
- [ ] Health checks working

### Monitoring & Maintenance

```bash
# View logs
docker-compose logs -f api
docker-compose logs -f web

# Database backup
docker-compose exec db pg_dump -U leasepeace leasepeace > backup_$(date +%Y%m%d).sql

# Restore database
cat backup.sql | docker-compose exec -T db psql -U leasepeace leasepeace

# Update application
git pull
docker-compose up -d --build
docker-compose exec api alembic upgrade head
```

### Scaling Considerations

For production scale:
1. **Database**: Use managed PostgreSQL with read replicas
2. **Caching**: Add Redis for session storage
3. **CDN**: Use CloudFlare or CloudFront
4. **Load Balancing**: Multiple API instances behind load balancer
5. **Background Jobs**: Add Celery for async processing
6. **File Storage**: Use S3 for user uploads
7. **Search**: Add Elasticsearch for applicant search
