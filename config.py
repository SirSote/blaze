"""Social Media Bot Configuration"""

# API Endpoints
COMFYUI_URL = "http://localhost:8188"
OLLAMA_URL = "http://localhost:11434"
MIXPOST_URL = "http://localhost:9000"

# Target Platforms
PLATFORMS = ["instagram", "facebook", "twitter", "pinterest"]

# Posting Schedule
POST_TIME = "10:00"  # Best engagement time

# File Paths
PRODUCTS_FILE = "/home/sirsote/scripts/social-bot/products.json"
OUTPUT_DIR = "/home/sirsote/scripts/social-bot/output/images/"
WORKFLOW_FILE = "/home/sirsote/scripts/social-bot/workflows/comfyui_template.json"
LOG_FILE = "/home/sirsote/scripts/social-bot/social-bot.log"
