from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Stability AI settings
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY", "your-api-key-here")
STABILITY_API_URL = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

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

    prompt = f"A high-quality studio photo of {product} styled as {style_clean or 'casual wear'} on a white background"

    files = {
        "prompt": (None, prompt),
        "output_format": (None, "jpeg")  # 🔥 Must be jpeg or png now
    }

    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "application/json"
    }

    try:
        print("🎯 Prompt:", prompt)
        print("📡 Posting to:", STABILITY_API_URL)

        response = requests.post(STABILITY_API_URL, headers=headers, files=files)

        if response.status_code != 200:
            print("❌ Stability error:", response.text)
            return jsonify({
                "error": "Stability AI error",
                "details": response.text
            }), 500

        result = response.json()
        image_url = result.get("image")

        if not image_url:
            return jsonify({"error": "No image returned"}), 500

        return jsonify({
            "image_url": image_url,
            "prompt_used": prompt
        })

    except Exception as e:
        print("🔥 Exception:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
