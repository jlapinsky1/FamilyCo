from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Stability AI API configuration
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY") or "your-api-key-here"
STABILITY_API_URL = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024x1024/text-to-image"

HEADERS = {
    "Authorization": f"Bearer {STABILITY_API_KEY}",
    "Content-Type": "application/json"
}

@app.route("/generate-images", methods=["POST"])
def generate_images():
    data = request.get_json()

    # Accept a single object or array of one
    if isinstance(data, dict):
        data = [data]
    if not data:
        return jsonify({"error": "Missing input"}), 400

    item = data[0]
    product = item.get("product", "toddler jogger pants")
    style = item.get("style", "")
    style_clean = style.replace("_", " ").replace("-", " ").strip()

    # Build the prompt
    prompt = f"A high-quality studio photo of {product} styled as {style_clean or 'casual wear'} on a white background"

    # Build payload for Stability AI
    payload = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 7,
        "clip_guidance_preset": "FAST_BLUE",
        "height": 1024,
        "width": 1024,
        "samples": 1,
        "steps": 30
    }

    try:
        print("Sending prompt:", prompt)
        response = requests.post(STABILITY_API_URL, headers=HEADERS, json=payload)

        if response.status_code != 200:
            print("Stability API error:", response.text)
            return jsonify({
                "error": "Stability AI error",
                "details": response.text
            }), 500

        result = response.json()
        artifact = result.get("artifacts", [])[0]

        if artifact.get("finishReason") != "SUCCESS":
            return jsonify({"error": "Image generation failed", "reason": artifact.get("finishReason")}), 500

        return jsonify({
            "base64_image": artifact["base64"],
            "prompt_used": prompt
        })

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
