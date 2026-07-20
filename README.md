# Blaze — Autonomous Social Media Agent

🔥 **Status:** 80% Complete | Blocked on social account OAuth

## Overview
Fully automated social media content creation and posting system. AI generates product images and captions, then schedules posts across Instagram, Facebook, Twitter, TikTok, LinkedIn, and Pinterest.

## Architecture
```
CRON (daily 9am)
  ↓
ComfyUI (image generation)
  ↓
Ollama (caption generation)
  ↓
Mixpost (schedule post)
  ↓
Social platforms (publish)
```

## Tech Stack
- **Image Generation:** ComfyUI (Docker) with SDXL/DreamShaper models
- **Caption Generation:** Ollama (localhost:11434) with llama3.x
- **Scheduling:** Mixpost (Docker) with MariaDB + Redis
- **Orchestration:** Python scripts
- **Automation:** Cron (daily)

## Services
- ComfyUI: http://localhost:8188
- Ollama: http://localhost:11434
- Mixpost: http://localhost:9000

## Scripts
- `config.py` — Configuration
- `generate_image.py` — ComfyUI image generation
- `write_caption.py` — Ollama caption generation
- `schedule_post.py` — Mixpost API scheduling
- `daily_workflow.py` — Full workflow orchestration

## Setup

### 1. Start Services
```bash
docker-compose up -d
```

### 2. Configure Mixpost
```bash
# Visit http://localhost:9000
# Create admin account
# Connect social accounts (Facebook, Instagram, Twitter, etc.)
```

### 3. Add Products
```bash
# Edit products.json with your product catalog
nano products.json
```

### 4. Test Workflow
```bash
python daily_workflow.py
```

### 5. Enable Cron Automation
```bash
crontab -e
# Add: 0 9 * * * /usr/bin/python3 ~/scripts/social-bot/daily_workflow.py
```

## Features
- [x] Image generation with ComfyUI
- [x] AI caption generation with Ollama
- [x] Mixpost scheduling integration
- [x] Product catalog system
- [x] Full workflow orchestration
- [ ] Social accounts connected
- [ ] Cron automation enabled
- [ ] End-to-end live testing

## Roadmap
- [ ] Connect Facebook/Instagram accounts in Mixpost
- [ ] Add real product catalog
- [ ] Enable daily cron automation
- [ ] A/B testing for captions
- [ ] Analytics dashboard
- [ ] Multi-language support

## Cost
**$0/month** (fully self-hosted)

## Project Status
All infrastructure is built and tested. Waiting on social account OAuth connection to go live with automated posting.

---

**Built by SirSote** | [Portfolio](https://sirsote.com) | [GitHub](https://github.com/SirSote)
