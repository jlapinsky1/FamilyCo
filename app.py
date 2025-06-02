from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY") or "your-api-key-here"
STABILITY_API_URL = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024x1024/text-to-image"

HEADERS = {
    "Authorization": f"Bearer {STABILITY_API_KEY}",
    "Content-Type": "application/json"
}

@app.route("/generate-images", methods=["POST"])
def generate_images():
    data = request.get_json()

    # Normalize input
    if isinstance(data, dict):
        data = [data]
    if not data:
        return jsonify({"error": "Missing input"}), 400

    item = data[0]
    product = item.get("product", "toddler jogger pants")
    style = item.get("style", "")
    prompt = f"A product photo of {product} in {style.replace('_', ' ').replace('-', ' ')} on a plain background"

    payload = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 7,
        "clip_guidance_preset": "FAST_BLUE",
        "height": 512,
        "width": 512,
        "samples": 1,
        "steps": 30
    }

    try:
        print("Prompt:", prompt)
        response = requests.post(STABILITY_API_URL, headers=HEADERS, json=payload)
        if response.status_code != 200:
            print("Stability error:", response.text)
            return jsonify({"error": "Stability AI error", "details": response.text}), 500

        response_json = response.json()
        artifact = response_json["artifacts"][0]
        if artifact["finishReason"] != "SUCCESS":
            return jsonify({"error": "Image generation failed", "reason": artifact["finishReason"]}), 500

        return jsonify({
            "base64_image": artifact["base64"],
            "prompt_used": prompt
        })

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
