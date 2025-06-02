from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Stability AI config
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY") or "your-api-key-here"
STABILITY_API_URL = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

HEADERS = {
    "Authorization": f"Bearer {STABILITY_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
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
    style_clean = style.replace("_", " ").replace("-", " ").strip()

    prompt = f"A high-quality studio photo of {product} styled as {style_clean or 'casual wear'} on a white background"

    payload = {
        "prompt": prompt,
        "output_format": "base64_json"
    }

    try:
        print("🔁 Sending prompt:", prompt)
        print("🔗 Endpoint:", STABILITY_API_URL)

        response = requests.post(STABILITY_API_URL, headers=HEADERS, json=payload)

        if response.status_code != 200:
            print("❌ Stability API error:", response.text)
            return jsonify({
                "error": "Stability AI error",
                "details": response.text
            }), 500

        result = response.json()
        image_base64 = result.get("image")

        if not image_base64:
            return jsonify({"error": "No image returned"}), 500

        return jsonify({
            "base64_image": f"data:image/jpeg;base64,{image_base64}",
            "prompt_used": prompt
        })

    except Exception as e:
        print("🔥 Exception occurred:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
