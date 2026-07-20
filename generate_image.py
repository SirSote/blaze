"""Generate images using ComfyUI API"""

import requests
import json
import time
import uuid
from pathlib import Path
from config import COMFYUI_URL, OUTPUT_DIR, WORKFLOW_FILE


def load_workflow():
    """Load the ComfyUI workflow template"""
    with open(WORKFLOW_FILE) as f:
        return json.load(f)


def queue_prompt(workflow: dict) -> str:
    """Queue a prompt in ComfyUI and return the prompt_id"""
    client_id = str(uuid.uuid4())
    response = requests.post(
        f"{COMFYUI_URL}/prompt",
        json={"prompt": workflow, "client_id": client_id}
    )
    response.raise_for_status()
    return response.json()["prompt_id"]


def wait_for_completion(prompt_id: str, timeout: int = 300) -> dict:
    """Wait for the image generation to complete"""
    start = time.time()
    while time.time() - start < timeout:
        response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}")
        if response.status_code == 200:
            history = response.json()
            if prompt_id in history:
                return history[prompt_id]
        time.sleep(2)
    raise TimeoutError(f"Generation timed out after {timeout}s")


def download_image(history: dict, filename: str) -> str:
    """Download the generated image from ComfyUI"""
    # Find the output image in history
    outputs = history.get("outputs", {})
    for node_id, node_output in outputs.items():
        if "images" in node_output:
            image_data = node_output["images"][0]
            image_filename = image_data["filename"]
            subfolder = image_data.get("subfolder", "")

            # Download the image
            params = {"filename": image_filename, "subfolder": subfolder, "type": "output"}
            response = requests.get(f"{COMFYUI_URL}/view", params=params)
            response.raise_for_status()

            # Save to output directory
            output_path = Path(OUTPUT_DIR) / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(response.content)

            return str(output_path)

    raise ValueError("No image found in generation output")


def generate(prompt: str, filename: str) -> str:
    """
    Generate an image using ComfyUI

    Args:
        prompt: The text prompt for image generation
        filename: Output filename (e.g., "post_20260214.png")

    Returns:
        Path to the generated image
    """
    # Load and modify workflow
    workflow = load_workflow()

    # Update the positive prompt in the workflow
    # This assumes a standard SDXL workflow structure
    for node_id, node in workflow.items():
        if node.get("class_type") == "CLIPTextEncode":
            if "positive" in node.get("_meta", {}).get("title", "").lower():
                node["inputs"]["text"] = prompt
                break
        # Fallback: look for text input
        if "text" in node.get("inputs", {}):
            if isinstance(node["inputs"]["text"], str):
                node["inputs"]["text"] = prompt
                break

    # Queue the generation
    prompt_id = queue_prompt(workflow)
    print(f"Queued generation: {prompt_id}")

    # Wait for completion
    history = wait_for_completion(prompt_id)
    print("Generation complete")

    # Download the image
    output_path = download_image(history, filename)
    print(f"Saved to: {output_path}")

    return output_path


if __name__ == "__main__":
    # Test generation
    test_prompt = "professional product photo of a t-shirt, studio lighting, white background"
    result = generate(test_prompt, "test_image.png")
    print(f"Generated: {result}")
