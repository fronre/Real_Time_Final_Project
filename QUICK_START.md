# 🚀 Quick Start Guide - Docker Setup

## For Your Friends - Super Easy Setup!

### 📋 What You Need
1. **Docker Desktop** (free download)
2. **The project folder** (share this with friends)

### 🎯 3 Steps to Run

#### Step 1: Install Docker
Download from: https://www.docker.com/products/docker-desktop/

#### Step 2: Run These Commands
```bash
# Open terminal/command prompt in the project folder
cd Real_Time_Final_Project

# Build and start everything (this takes 2-3 minutes first time)
docker-compose up --build
```

#### Step 3: Open Browser
Go to: **http://localhost:3000**

🎉 **Done!** The trading dashboard is running!

---

## 📱 What You'll See

- **Live price charts** for 10 digital assets
- **Real-time trading signals** (BUY/SELL)
- **Trading statistics** (balance, profit, trades)
- **Microsecond timing** display
- **EDF task queue** visualization

---

## 🔧 If Something Goes Wrong

### Port Already Used?
```bash
docker-compose down
docker-compose up --build
```

### Build Failed?
```bash
docker system prune -f
docker-compose up --build
```

### Can't Connect?
1. Wait 30 seconds after starting
2. Try http://127.0.0.1:3000 instead of localhost:3000
3. Check if Docker Desktop is running

---

## 🛑 How to Stop

```bash
# Stop everything
docker-compose down

# Start again later
docker-compose up
```

---

## 📊 System Info

- **Frontend**: http://localhost:3000 (main dashboard)
- **API Status**: http://localhost:8000/health (server status)
- **All services start automatically**
- **Works on Windows, Mac, and Linux**

---

## 🎮 Share This With Friends

```
🚀 Real-Time Trading System

1. Install Docker: https://www.docker.com/products/docker-desktop/
2. Download the project folder
3. Run: docker-compose up --build
4. Open: http://localhost:3000

That's it! Enjoy the trading simulation! 🎉
```

---

## 🆘 Need Help?

Check the full guide: `DOCKER_SETUP.md`

Or try these commands:
```bash
# Check if services are running
docker-compose ps

# View logs
docker-compose logs

# Restart everything
docker-compose restart
```

**Happy Trading! 📈**
