# 🚀 Neo AI Global Deployment Guide

## 🎯 Quick Start

Neo AI is now fully configured and ready for global deployment! Choose your preferred method:

### 🔥 Method 1: Simple Start (Recommended for Testing)

```bash
# Start Neo AI without Docker
./start-simple.sh
```

This will:
- ✅ Start backend on port 8000
- ✅ Start frontend on port 3000
- ✅ Check health of both services
- ✅ Provide access URLs

### 🐳 Method 2: Docker Deployment (Production)

```bash
# For development
./deploy-global.sh

# For production
./deploy-global.sh prod
```

This will:
- ✅ Build and start all services with Docker
- ✅ Include Redis, RabbitMQ, and Nginx
- ✅ Set up health checks and monitoring
- ✅ Configure production-ready settings

## 🌍 Global Access Options

### 1. 🔗 Ngrok (Instant Global Access)

```bash
# Install ngrok (if not already installed)
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Create global tunnel
ngrok http 3000
```

**Result**: You'll get a public URL like `https://abc123.ngrok.io` that anyone can access worldwide!

### 2. ☁️ Cloud Deployment

Deploy to any cloud provider:

#### DigitalOcean
```bash
# Create droplet and run
git clone https://github.com/FRRWE3/my-private-repo.git
cd neo
./deploy-global.sh prod
```

#### AWS/Google Cloud
```bash
# Use docker-compose.prod.yml for production deployment
docker-compose -f docker-compose.prod.yml up -d
```

### 3. 🏠 Port Forwarding

Configure your router to forward port 3000 to your machine's local IP.

## 📋 System Status

### ✅ Backend Configuration
- **Environment**: Production
- **Supabase**: ✅ Configured
- **OpenRouter API**: ✅ Configured (DeepSeek R1)
- **Daytona Sandbox**: ✅ Configured
- **Health Check**: `/health` and `/api/health`

### ✅ Sandbox System
- **Mode**: Hybrid (Auto-fallback)
- **Daytona**: ✅ Available
- **Local Docker**: ✅ Ready (when Docker available)
- **Basic Mode**: ✅ Fallback option

### ✅ Frontend
- **Framework**: Next.js
- **Build**: ✅ Production ready
- **Environment**: Production

## 🔧 Configuration Files

### Backend (.env)
```bash
# All APIs configured:
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
OPENROUTER_API_KEY=your-openrouter-key
DAYTONA_API_KEY=your-daytona-key
SANDBOX_MODE=auto
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_VERCEL_ENV=production
```

## 🚀 Deployment Commands

### Start Services
```bash
# Simple mode (no Docker)
./start-simple.sh

# Docker mode
./deploy-global.sh

# Production Docker
./deploy-global.sh prod
```

### Stop Services
```bash
# Simple mode
kill $(cat .backend.pid .frontend.pid)

# Docker mode
docker-compose down
```

### View Logs
```bash
# Simple mode
tail -f backend/logs/agentpress_*.log

# Docker mode
docker-compose logs -f
```

## 🌐 Access URLs

### Local Access
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Global Access (with ngrok)
- **Public URL**: https://your-ngrok-id.ngrok.io
- **Secure HTTPS**: ✅ Automatic
- **Global CDN**: ✅ Included

## 🔒 Security Features

- ✅ CORS protection
- ✅ Rate limiting
- ✅ Health checks
- ✅ Secure headers
- ✅ Environment isolation
- ✅ API key protection

## 📊 Monitoring

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000

# Detailed API health
curl http://localhost:8000/api/health
```

### Service Status
```bash
# Check running processes
ps aux | grep -E "(uvicorn|npm)"

# Check ports
netstat -tlnp | grep -E "(3000|8000)"
```

## 🛠️ Troubleshooting

### Port Already in Use
```bash
# Find and kill process using port
sudo lsof -ti:3000 | xargs kill -9
sudo lsof -ti:8000 | xargs kill -9
```

### Backend Not Starting
```bash
# Check configuration
cd backend && python -c "from utils.config import config; print('Config OK')"

# Check dependencies
pip install -r requirements.txt
```

### Frontend Not Building
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

## 🎉 Success!

Neo AI is now ready for global access! The system includes:

- 🤖 **AI Agent**: DeepSeek R1 model with advanced reasoning
- 🛠️ **Code Execution**: Hybrid sandbox system (Daytona + Local)
- 🌐 **Global Access**: Multiple deployment options
- 📊 **Monitoring**: Health checks and logging
- 🔒 **Security**: Production-ready configuration

### Next Steps

1. **Test locally**: Access http://localhost:3000
2. **Enable global access**: Run `ngrok http 3000`
3. **Share the URL**: Give the ngrok URL to users worldwide
4. **Monitor usage**: Check logs and health endpoints
5. **Scale up**: Deploy to cloud for permanent hosting

**Your Neo AI system is now live and accessible globally! 🌍✨**