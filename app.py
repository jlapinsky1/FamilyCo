from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY") or "your-api-key-here"
STABILITY_API_URL = "https://api.stability.ai/v2beta/stable-image/generate/sd-xl"

HEADERS = {
    "Authorization": f"Bearer {STABILITY_API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

@app.route("/generate-images", methods=["POST"])
def generate_images():
    data = request.get_json()

    if isinstance(data, dict):
        data = [data]
    if not data:
        return jsonify({"error": "Missing input"}), 400

    item = data[0]
    product = item.get("product", "toddler jogger pants")
    style = item.get("style", "")
    style_clean = style.replace("_", " ").replace("-", " ").strip()

    prompt = f"Studio photo of {product} styled as {style_clean or 'casual wear'} on white background"

    payload = {
        "prompt": prompt,
        "output_format": "jpeg",
        "aspect_ratio": "1:1"
    }

    try:
        print("Sending prompt to Stability AI:", prompt)
        response = requests.post(STABILITY_API_URL, headers=HEADERS, json=payload)

        if response.status_code != 200:
            print("Stability API error:", response.text)
            return jsonify({"error": "Stability AI error", "details": response.text}), 500

        data = response.json()
        image_url = data.get("image")

        return jsonify({
            "image_url": image_url,
            "prompt_used": prompt
        })

    except Exception as e:
        print("Exception:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
