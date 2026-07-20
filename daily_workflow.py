#!/usr/bin/env python3
"""
Daily Social Media Bot
Runs via cron at 9am to generate and schedule posts
"""

import json
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path

from generate_image import generate
from write_caption import write_batch
from schedule_post import schedule_multi
from config import PLATFORMS, POST_TIME, PRODUCTS_FILE, LOG_FILE

# Set up logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def load_products() -> list:
    """Load products from JSON file"""
    with open(PRODUCTS_FILE) as f:
        return json.load(f)


def get_post_time() -> datetime:
    """Calculate the posting time for today"""
    hour, minute = map(int, POST_TIME.split(":"))
    post_dt = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)

    # If the time has passed, schedule for tomorrow
    if post_dt < datetime.now():
        post_dt += timedelta(days=1)

    return post_dt


def main():
    """Main workflow - runs daily"""
    logging.info("=" * 50)
    logging.info("Starting daily social media workflow")

    try:
        # 1. Load products
        products = load_products()
        logging.info(f"Loaded {len(products)} products")

        # 2. Pick a random product
        product = random.choice(products)
        logging.info(f"Selected product: {product['name']}")

        # 3. Generate image with ComfyUI
        date_str = datetime.now().strftime("%Y%m%d")
        image_prompt = f"professional product photo of {product['name']}, {product.get('style', 'modern')}, studio lighting, white background, high quality"
        image_filename = f"post_{date_str}_{product['id']}.png"

        logging.info(f"Generating image: {image_prompt[:50]}...")
        image_path = generate(image_prompt, image_filename)
        logging.info(f"Image saved: {image_path}")

        # 4. Write captions for each platform
        logging.info("Generating captions...")
        captions = write_batch(product, PLATFORMS)
        for platform, caption in captions.items():
            logging.info(f"{platform}: {caption[:50]}...")

        # 5. Schedule posts
        post_time = get_post_time()
        logging.info(f"Scheduling posts for {post_time}")
        results = schedule_multi(image_path, captions, post_time)

        # 6. Log results
        success = sum(1 for r in results if r["status"] == "scheduled")
        failed = len(results) - success
        logging.info(f"Scheduled: {success}, Failed: {failed}")

        for result in results:
            if result["status"] == "error":
                logging.error(f"{result['platform']}: {result['error']}")

        logging.info("Daily workflow complete!")
        print(f"Daily social media posts scheduled for {post_time}")
        print(f"  Product: {product['name']}")
        print(f"  Platforms: {success}/{len(PLATFORMS)} successful")

    except Exception as e:
        logging.error(f"Workflow failed: {e}")
        raise


if __name__ == "__main__":
    main()
