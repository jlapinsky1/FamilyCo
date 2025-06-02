from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Your Stability AI API Key
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY") or "your-api-key-here"
STABILITY_API_URL = "https://api.stability.ai/v2beta/stable-image/generate/sdxl"

HEADERS = {
    "Authorization": f"Bearer {STABILITY_API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

@app.route("/generate-images", methods=["POST"])
def generate_images():
    data = request.get_json()

    # Accept single object or array
    if isinstance(data, dict):
        data = [data]
    if not data:
        return jsonify({"error": "Missing input"}), 400

    item = data[0]
    age = item.get("age", "")
    product = item.get("product", "toddler jogger pants")
    style = item.get("style", "")

    # Clean the prompt
    style_desc = style.replace("_", " ").replace("-", " ").strip()
    prompt = f"A high-quality photo of {product} styled as {style_desc or 'modern casual wear'} on a white background"

    payload = {
        "prompt": prompt,
        "output_format": "jpeg",
        "aspect_ratio": "1:1"
    }

    try:
        print(f"Sending prompt to Stability: {prompt}")
        response = requests.post(STABILITY_API_URL, headers=HEADERS, json=payload)
        if response.status_code != 200:
            print("Stability error:", response.text)
            return jsonify({"error": "Stability AI error", "details": response.text}), 500

        image_data = response.json()
        return jsonify({
            "image_url": image_data.get("image", "No image returned"),
            "prompt_used": prompt
        })

    except Exception as e:
        print("Unexpected error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
