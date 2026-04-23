# Docker Setup Guide - Real-Time Trading System

## 🐳 Easy Docker Deployment for Your Friends

This guide helps you and your friends run the trading system easily using Docker, without any complex setup!

## 📋 Prerequisites

Only need to install **Docker** and **Docker Compose**:

### Windows
1. Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Restart your computer
3. Open PowerShell or Command Prompt as Administrator

### macOS
1. Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Restart your computer
3. Open Terminal

### Linux (Ubuntu/Debian)
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

## 🚀 Quick Start (3 Commands Only!)

### Step 1: Download the Project
```bash
# Extract the project folder
# Open terminal/command prompt in the project folder
cd Real_Time_Final_Project
```

### Step 2: Build and Run
```bash
# Build all containers and start the system
docker-compose up --build
```

### Step 3: Open Browser
Open your web browser and go to: **http://localhost:3000**

That's it! 🎉 The system is now running!

## 📱 Access Points

| Service | URL | Description |
|--------|-----|-------------|
| **Trading Dashboard** | http://localhost:3000 | Main web interface |
| **API Health Check** | http://localhost:8000/health | Server status |
| **Trading Positions** | http://localhost:8000/positions | Current positions |
| **Bot Port** | localhost:8080 | C bot (internal) |

## 🔧 Advanced Commands

### Stop the System
```bash
docker-compose down
```

### Restart the System
```bash
docker-compose restart
```

### View Logs
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs bot
docker-compose logs server
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f
```

### Update the System
```bash
# Stop and remove containers
docker-compose down

# Rebuild with latest changes
docker-compose up --build --force-recreate
```

## 🛠️ Troubleshooting

### Port Already in Use
```bash
# Check what's using the ports
netstat -tulpn | grep :8000
netstat -tulpn | grep :8080
netstat -tulpn | grep :3000

# Kill processes using ports (Linux/Mac)
sudo kill -9 <PID>

# Stop other Docker containers
docker-compose down
docker system prune -f
```

### Permission Issues (Linux/Mac)
```bash
# Fix Docker permissions
sudo chmod 666 /var/run/docker.sock

# Or add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Build Failures
```bash
# Clean build cache
docker-compose down
docker system prune -a -f
docker-compose up --build
```

### Container Won't Start
```bash
# Check container status
docker-compose ps

# Check detailed logs
docker-compose logs <service-name>

# Restart specific service
docker-compose restart <service-name>
```

## 📦 What Docker Does For You

### ✅ Automatic Setup
- **No need to install GCC, Python, or dependencies**
- **No configuration required**
- **Works the same on Windows, Mac, and Linux**
- **All services connected automatically**

### ✅ Isolated Environment
- **Won't interfere with your system**
- **Safe to run alongside other projects**
- **Easy to stop and remove completely**

### ✅ Easy Sharing
- **Just share the project folder**
- **Friends run with 3 commands**
- **No technical knowledge needed**

## 🎮 How Your Friends Can Use It

### Send Them This:
```
🚀 Real-Time Trading System - Docker Setup

1. Install Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Download and extract the project folder
3. Open terminal/command prompt in the folder
4. Run: docker-compose up --build
5. Open browser: http://localhost:3000

That's it! The trading dashboard will appear automatically. 🎉
```

## 📊 System Architecture in Docker

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Python Server │    │     C Bot       │
│   (nginx)       │◄──►│   (FastAPI)     │◄──►│   (market_bot)  │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 8080    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Docker Network  │
                    │ 172.20.0.0/16   │
                    └─────────────────┘
```

## 🔍 Monitoring

### Check System Health
```bash
# Check all services
docker-compose ps

# Check resource usage
docker stats

# Check health status
curl http://localhost:8000/health
```

### Real-time Monitoring
```bash
# Watch logs live
docker-compose logs -f

# Monitor specific service
docker-compose logs -f server
```

## 🎯 Performance Tips

### For Better Performance
```bash
# Allocate more memory to Docker (Docker Desktop settings)
# Recommended: 4GB RAM, 2 CPU cores

# Use production build
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

### For Development
```bash
# Mount source code for live updates
docker-compose up --build --volume ./server:/app
```

## 🆘 Getting Help

### Common Issues & Solutions

1. **"Docker command not found"**
   - Install Docker Desktop first
   - Restart your computer

2. **"Port already in use"**
   - Run `docker-compose down`
   - Check other applications using ports 8000, 8080, 3000

3. **"Build failed"**
   - Check internet connection
   - Run `docker system prune -f`
   - Try again with `docker-compose up --build`

4. **"Can't connect to localhost"**
   - Wait 30 seconds after starting
   - Check `docker-compose ps` to see if services are running
   - Try http://127.0.0.1:3000 instead of localhost

### Need More Help?
- Check the logs: `docker-compose logs`
- Restart everything: `docker-compose restart`
- Start fresh: `docker-compose down && docker-compose up --build`

## 🎉 Success!

When you see this in your browser, it's working:

- **Green "Connected" status**
- **Live price updates**
- **Trading statistics**
- **Real-time charts**

Your friends can now run the trading system with just Docker - no technical setup needed! 🚀
