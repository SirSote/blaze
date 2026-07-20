"""Schedule posts using Mixpost API"""

import requests
from datetime import datetime
from pathlib import Path
from config import MIXPOST_URL


def get_accounts() -> list:
    """Get connected social media accounts from Mixpost"""
    response = requests.get(f"{MIXPOST_URL}/api/accounts")
    if response.status_code == 200:
        return response.json().get("data", [])
    return []


def upload_media(image_path: str) -> str:
    """Upload an image to Mixpost and return the media ID"""
    with open(image_path, "rb") as f:
        files = {"file": (Path(image_path).name, f, "image/png")}
        response = requests.post(f"{MIXPOST_URL}/api/media", files=files)
        response.raise_for_status()
        return response.json().get("id")


def schedule(image_path: str, caption: str, platforms: list, post_time: datetime) -> dict:
    """
    Schedule a post in Mixpost

    Args:
        image_path: Path to the image file
        caption: The post caption/content
        platforms: List of platform names to post to
        post_time: When to publish the post

    Returns:
        API response with post details
    """
    # Upload the image first
    media_id = upload_media(image_path)

    # Get account IDs for the requested platforms
    accounts = get_accounts()
    account_ids = []
    for account in accounts:
        if account.get("provider", "").lower() in [p.lower() for p in platforms]:
            account_ids.append(account["id"])

    if not account_ids:
        raise ValueError(f"No connected accounts found for platforms: {platforms}")

    # Create the scheduled post
    post_data = {
        "body": caption,
        "media": [media_id],
        "accounts": account_ids,
        "scheduled_at": post_time.isoformat(),
        "status": "scheduled"
    }

    response = requests.post(
        f"{MIXPOST_URL}/api/posts",
        json=post_data
    )
    response.raise_for_status()

    result = response.json()
    print(f"Scheduled post for {post_time} on {len(account_ids)} accounts")
    return result


def schedule_multi(image_path: str, captions: dict, post_time: datetime) -> list:
    """
    Schedule posts to multiple platforms with platform-specific captions

    Args:
        image_path: Path to the image file
        captions: Dict of {platform: caption}
        post_time: When to publish

    Returns:
        List of API responses
    """
    results = []
    for platform, caption in captions.items():
        try:
            result = schedule(image_path, caption, [platform], post_time)
            results.append({"platform": platform, "status": "scheduled", "data": result})
        except Exception as e:
            results.append({"platform": platform, "status": "error", "error": str(e)})
    return results


if __name__ == "__main__":
    # Test - list connected accounts
    print("Connected accounts:")
    for account in get_accounts():
        print(f"  - {account.get('provider')}: {account.get('name')}")
