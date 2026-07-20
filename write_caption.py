"""Generate captions using Ollama API"""

import requests
from config import OLLAMA_URL


def write(product: dict, platform: str) -> str:
    """
    Generate a caption for a social media post

    Args:
        product: Dict with 'name', 'description', 'price' keys
        platform: Target platform (instagram, facebook, twitter, pinterest)

    Returns:
        Generated caption with hashtags
    """
    # Platform-specific guidelines
    guidelines = {
        "instagram": "Keep under 150 chars. Use emojis. Include 5 relevant hashtags at the end.",
        "facebook": "Keep under 200 chars. Be conversational. Include a call-to-action.",
        "twitter": "Keep under 280 chars. Be punchy and direct. Use 2-3 hashtags.",
        "pinterest": "Keep under 100 chars. Focus on the visual appeal. Use descriptive keywords.",
        "tiktok": "Keep under 100 chars. Be trendy and casual. Use trending hashtags.",
        "linkedin": "Keep professional. Focus on value proposition. Use 3 hashtags."
    }

    guide = guidelines.get(platform, guidelines["instagram"])

    prompt = f"""Write a {platform} caption for this product:

Product: {product.get('name', 'Custom T-Shirt')}
Description: {product.get('description', 'High-quality custom design')}
Price: {product.get('price', '$25')}

Guidelines: {guide}

Write ONLY the caption, nothing else. No quotes or explanations."""

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": "tinyllama",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 200
            }
        },
        timeout=60
    )
    response.raise_for_status()

    caption = response.json().get("response", "").strip()
    return caption


def write_batch(product: dict, platforms: list) -> dict:
    """Generate captions for multiple platforms"""
    captions = {}
    for platform in platforms:
        captions[platform] = write(product, platform)
    return captions


if __name__ == "__main__":
    # Test caption generation
    test_product = {
        "name": "Vintage Rock Band T-Shirt",
        "description": "Classic 80s rock band design on premium cotton",
        "price": "$29.99"
    }

    for platform in ["instagram", "facebook", "twitter"]:
        print(f"\n{platform.upper()}:")
        caption = write(test_product, platform)
        print(caption)
