# Roastify Pro - Complete Troubleshooting Guide

## Quick Solutions Index

### 🚨 EMERGENCY ISSUES

#### 1. Bot Not Responding
✅ QUICK FIX:
docker-compose restart bot
docker-compose logs --tail=100 bot

🔍 DIAGNOSE:

Check bot token in .env

Verify internet connection

Check Telegram API status


#### 2. Database Connection Failed

QUICK FIX:
docker-compose restart db
docker-compose exec db psql -U postgres -c "SELECT 1;"

🔍 DIAGNOSE:

Check POSTGRES_PASSWORD in .env

Verify disk space

Check database logs


#### 3. High Memory Usage


✅ QUICK FIX:
docker-compose restart
docker system prune -f

🔍 DIAGNOSE:

Check with: docker stats

Clear Redis: redis-cli FLUSHALL

Increase swap space


### 🔧 COMMON ISSUES

#### Image Generation Failed
**Symptoms:**
- Error: "Image processing failed"
- Timeout errors
- Blank images

**Solutions:**
```bash
# 1. Clear image cache
docker-compose exec redis redis-cli --scan --pattern "image:*" | xargs redis-cli DEL

# 2. Reinstall Pillow
docker-compose exec bot pip install --upgrade Pillow

# 3. Check disk space
df -h /tmp

# 4. Increase timeout
# Edit .env: IMAGE_GENERATION_TIMEOUT=30


