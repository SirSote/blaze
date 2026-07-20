# Social Media Bot - Complete Documentation

## Overview

Fully automated social media content creation and posting system using AI-generated images and captions. Zero monthly cost - all self-hosted.

**Created:** 2026-02-14
**Status:** OPERATIONAL
**Monthly Cost:** $0

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   CRON JOB  │────▶│  COMFYUI    │────▶│   OLLAMA    │────▶│   MIXPOST   │
│  (9am daily)│     │ (images)    │     │ (captions)  │     │ (scheduling)│
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                   │                   │
                           ▼                   ▼                   ▼
                    localhost:8188      localhost:11434     localhost:9000
```

---

## Services

### 1. ComfyUI (AI Image Generation)
- **URL:** http://localhost:8188
- **Status:** Running in Docker
- **Container:** comfyui
- **Purpose:** Generate product photos, ads, social media graphics
- **Models Available:**
  - `sd_xl_base_1.0.safetensors` (SDXL - high quality)
  - `dreamshaper_8.safetensors` (artistic styles)
- **API Endpoints:**
  - `POST /prompt` - Queue image generation
  - `GET /history/{prompt_id}` - Check generation status
  - `GET /view?filename=X` - Download generated image

### 2. Ollama (AI Text Generation)
- **URL:** http://localhost:11434
- **Status:** Running as service
- **Binary:** /home/sirsote/.local/bin/ollama
- **Purpose:** Write captions, hashtags, CTAs for each platform
- **Models Available:**
  - `tinyllama` (637MB) - ACTIVE, fast, low memory
  - `llama3.1:8b` (4.9GB) - Better quality, needs more RAM
  - `llama3.2:3b` (2.0GB) - Medium quality
- **API Endpoints:**
  - `POST /api/generate` - Generate text
  - `POST /api/chat` - Chat completion
  - `GET /api/tags` - List models
- **Start Command:** `ollama serve`

### 3. Mixpost (Social Media Scheduler)
- **URL:** http://localhost:9000
- **Status:** Running in Docker
- **Containers:**
  - `mixpost` (web app)
  - `mixpost_db` (MariaDB database)
- **Network:** mixpost_network
- **Purpose:** Schedule and auto-post to all platforms
- **Supported Platforms:**
  - Instagram
  - Facebook
  - Twitter/X
  - TikTok
  - LinkedIn
  - Pinterest
- **Database Credentials:**
  - Host: mixpost_db
  - Database: mixpost
  - Username: mixpost
  - Password: mixpost_password
- **API Endpoints:**
  - `GET /api/accounts` - List connected accounts
  - `POST /api/media` - Upload image
  - `POST /api/posts` - Create/schedule post

---

## File Structure

```
/home/sirsote/scripts/social-bot/
├── config.py                 # All configuration settings
├── generate_image.py         # ComfyUI API wrapper
├── write_caption.py          # Ollama API wrapper
├── schedule_post.py          # Mixpost API wrapper
├── daily_workflow.py         # Main orchestrator (runs daily)
├── products.json             # Product catalog
├── docker-compose.yml        # Docker configuration
├── README.md                 # This file
├── social-bot.log            # Activity log (created on first run)
├── workflows/
│   └── comfyui_template.json # ComfyUI workflow for image generation
└── output/
    └── images/               # Generated images saved here
```

---

## Configuration (config.py)

```python
# API Endpoints
COMFYUI_URL = "http://localhost:8188"
OLLAMA_URL = "http://localhost:11434"
MIXPOST_URL = "http://localhost:9000"

# Target Platforms
PLATFORMS = ["instagram", "facebook", "twitter", "pinterest"]

# Posting Schedule
POST_TIME = "10:00"  # When posts go live

# File Paths
PRODUCTS_FILE = "/home/sirsote/scripts/social-bot/products.json"
OUTPUT_DIR = "/home/sirsote/scripts/social-bot/output/images/"
WORKFLOW_FILE = "/home/sirsote/scripts/social-bot/workflows/comfyui_template.json"
LOG_FILE = "/home/sirsote/scripts/social-bot/social-bot.log"
```

---

## Products Catalog (products.json)

Add your wife's actual products here:

```json
[
  {
    "id": "shirt001",
    "name": "Vintage Rock Band T-Shirt",
    "description": "Classic 80s rock band design on premium cotton",
    "price": "$29.99",
    "style": "vintage retro 80s aesthetic"
  },
  {
    "id": "shirt002",
    "name": "Minimalist Quote Tee",
    "description": "Inspirational quote in elegant typography",
    "price": "$24.99",
    "style": "minimalist clean modern"
  }
]
```

**Fields:**
- `id` - Unique product identifier
- `name` - Product name (used in image prompt and caption)
- `description` - Product description (used in caption)
- `price` - Display price (used in caption)
- `style` - Visual style keywords (used in image prompt)

---

## Scripts Detail

### generate_image.py
Generates product images using ComfyUI's API.

**Functions:**
- `load_workflow()` - Loads the ComfyUI workflow template
- `queue_prompt(workflow)` - Sends workflow to ComfyUI, returns prompt_id
- `wait_for_completion(prompt_id, timeout=300)` - Polls until image is ready
- `download_image(history, filename)` - Downloads and saves the image
- `generate(prompt, filename)` - Main function, returns path to saved image

**Usage:**
```python
from generate_image import generate
image_path = generate("product photo of vintage t-shirt", "post_20260214.png")
```

### write_caption.py
Generates platform-specific captions using Ollama.

**Functions:**
- `write(product, platform)` - Generate caption for one platform
- `write_batch(product, platforms)` - Generate captions for multiple platforms

**Platform Guidelines:**
- Instagram: Under 150 chars, emojis, 5 hashtags
- Facebook: Under 200 chars, conversational, CTA
- Twitter: Under 280 chars, punchy, 2-3 hashtags
- Pinterest: Under 100 chars, descriptive keywords
- TikTok: Under 100 chars, trendy, trending hashtags
- LinkedIn: Professional, value-focused, 3 hashtags

**Usage:**
```python
from write_caption import write, write_batch

product = {"name": "Cool Tee", "description": "Awesome design", "price": "$25"}
caption = write(product, "instagram")
# or
captions = write_batch(product, ["instagram", "facebook", "twitter"])
```

### schedule_post.py
Schedules posts to social media via Mixpost API.

**Functions:**
- `get_accounts()` - List connected social accounts
- `upload_media(image_path)` - Upload image, returns media_id
- `schedule(image_path, caption, platforms, post_time)` - Schedule single post
- `schedule_multi(image_path, captions, post_time)` - Schedule to multiple platforms

**Usage:**
```python
from schedule_post import schedule, schedule_multi
from datetime import datetime

# Single platform
schedule("/path/to/image.png", "Caption here", ["instagram"], datetime.now())

# Multiple platforms with different captions
captions = {"instagram": "IG caption", "facebook": "FB caption"}
schedule_multi("/path/to/image.png", captions, datetime.now())
```

### daily_workflow.py
Main orchestrator that runs the full workflow.

**Workflow:**
1. Load products from products.json
2. Pick a random product
3. Generate image with ComfyUI
4. Write captions for each platform with Ollama
5. Schedule posts via Mixpost
6. Log results

**Usage:**
```bash
# Manual run
python3 /home/sirsote/scripts/social-bot/daily_workflow.py

# Via cron (automated daily at 9am)
0 9 * * * python3 /home/sirsote/scripts/social-bot/daily_workflow.py
```

---

## Docker Commands

### Check Status
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Start Services
```bash
# Start ComfyUI (if not running)
docker start comfyui

# Start Mixpost stack
docker start mixpost_db
docker start mixpost

# Start Ollama
ollama serve
```

### Stop Services
```bash
docker stop mixpost mixpost_db
pkill ollama
```

### View Logs
```bash
docker logs mixpost
docker logs mixpost_db
docker logs comfyui
```

### Restart Services
```bash
docker restart mixpost
docker restart mixpost_db
docker restart comfyui
```

### Remove and Recreate Mixpost
```bash
docker stop mixpost mixpost_db
docker rm mixpost mixpost_db
docker volume rm mixpost_storage mixpost_db_data
# Then run the docker run commands again
```

---

## Cron Setup

Edit crontab:
```bash
crontab -e
```

Add this line to run daily at 9am:
```
0 9 * * * /usr/bin/python3 /home/sirsote/scripts/social-bot/daily_workflow.py >> /home/sirsote/scripts/social-bot/cron.log 2>&1
```

**Cron Format:** `minute hour day month weekday command`
- `0 9 * * *` = Every day at 9:00 AM
- `0 9,18 * * *` = Every day at 9am and 6pm
- `0 9 * * 1-5` = Weekdays only at 9am

---

## Mixpost Setup (First Time)

1. **Open browser:** http://localhost:9000
2. **Create admin account** (first visit)
3. **Connect social accounts:**
   - Go to Settings → Social Accounts
   - Click "Add Account"
   - Select platform (Instagram, Facebook, etc.)
   - Authorize with your credentials
4. **Note:** Some platforms (Instagram, TikTok) require business accounts for API access

---

## Testing

### Test Ollama (Caption Generation)
```bash
curl -s http://localhost:11434/api/generate \
  -d '{"model":"tinyllama","prompt":"Write an Instagram caption for a vintage t-shirt","stream":false}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('response',''))"
```

### Test ComfyUI (Image Generation)
```bash
curl -s http://localhost:8188/system_stats
```

### Test Mixpost
```bash
curl -s http://localhost:9000 -o /dev/null -w "%{http_code}"
# Should return 302 (redirect to login)
```

### Test Full Caption Script
```bash
cd /home/sirsote/scripts/social-bot
python3 -c "
from write_caption import write
product = {'name': 'Test Shirt', 'description': 'Cool design', 'price': '\$25'}
print(write(product, 'instagram'))
"
```

---

## Troubleshooting

### Ollama "not enough memory" error
The larger models (llama3.1:8b, llama3.2:3b) need more RAM. Solutions:
1. Use `tinyllama` (current config) - only needs ~1GB
2. Close other applications to free RAM
3. Use CPU-only mode: Set `OLLAMA_CPU=1` environment variable

### Mixpost not starting
Check if database is ready:
```bash
docker logs mixpost_db
```
Wait 30 seconds after starting mixpost_db before starting mixpost.

### ComfyUI workflow errors
1. Check if models exist: `ls /home/sirsote/AI/ComfyUI/models/checkpoints/`
2. Update workflow template to use correct model name
3. View ComfyUI logs: `docker logs comfyui`

### Posts not publishing
1. Verify accounts are connected in Mixpost dashboard
2. Check Mixpost logs: `docker logs mixpost`
3. Some platforms require business accounts for API access

### Images not generating
1. Ensure ComfyUI is running: `docker ps | grep comfyui`
2. Check GPU/memory availability
3. Try simpler prompt first

---

## Customization

### Change Posting Time
Edit `config.py`:
```python
POST_TIME = "10:00"  # Change to desired time (24h format)
```

### Add More Platforms
Edit `config.py`:
```python
PLATFORMS = ["instagram", "facebook", "twitter", "pinterest", "linkedin", "tiktok"]
```

### Use Better AI Model (if you have RAM)
Edit `write_caption.py`:
```python
"model": "llama3.1:8b",  # Instead of "tinyllama"
```

### Change Image Style
Edit `daily_workflow.py`, modify the prompt:
```python
image_prompt = f"your custom prompt here with {product['name']}"
```

### Add More Products
Edit `products.json` and add entries following the same format.

---

## API Reference

### ComfyUI API
```
Base URL: http://localhost:8188

POST /prompt
Body: {"prompt": {workflow_json}, "client_id": "uuid"}
Response: {"prompt_id": "uuid"}

GET /history/{prompt_id}
Response: {prompt_id: {outputs: {...}}}

GET /view?filename=X&type=output
Response: Image binary
```

### Ollama API
```
Base URL: http://localhost:11434

POST /api/generate
Body: {"model": "tinyllama", "prompt": "text", "stream": false}
Response: {"response": "generated text"}

GET /api/tags
Response: {"models": [...]}
```

### Mixpost API
```
Base URL: http://localhost:9000

GET /api/accounts
Response: {"data": [{id, provider, name}]}

POST /api/media
Body: multipart/form-data with file
Response: {"id": "media_id"}

POST /api/posts
Body: {"body": "caption", "media": ["id"], "accounts": [ids], "scheduled_at": "ISO8601"}
Response: {post details}
```

---

## Backup

### Backup Products
```bash
cp /home/sirsote/scripts/social-bot/products.json /home/sirsote/scripts/social-bot/products.json.backup
```

### Backup Mixpost Data
```bash
docker run --rm -v mixpost_db_data:/data -v $(pwd):/backup alpine tar czf /backup/mixpost_db_backup.tar.gz /data
```

### Backup Generated Images
```bash
tar czf social-bot-images-$(date +%Y%m%d).tar.gz /home/sirsote/scripts/social-bot/output/
```

---

## Logs

### Application Log
```bash
tail -f /home/sirsote/scripts/social-bot/social-bot.log
```

### Cron Log
```bash
tail -f /home/sirsote/scripts/social-bot/cron.log
```

### Service Logs
```bash
docker logs -f mixpost
docker logs -f comfyui
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Check all services | `docker ps` |
| Start Ollama | `ollama serve` |
| Run manually | `python3 ~/scripts/social-bot/daily_workflow.py` |
| View logs | `tail -f ~/scripts/social-bot/social-bot.log` |
| Edit products | `nano ~/scripts/social-bot/products.json` |
| Open Mixpost | http://localhost:9000 |
| Open ComfyUI | http://localhost:8188 |

---

## Support

- **Vault Location:** /home/sirsote/Documents/.sote/agent-bizz/
- **Diagrams:** social-media-architecture.drawio, social-media-zero-cost-architecture.drawio
- **Related Projects:** Echo-Zero (client intake bot)

---

*Last Updated: 2026-02-14*
