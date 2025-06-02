
from flask import Flask, request, jsonify
import openai
import os
import base64

app = Flask(__name__)

# Set your OpenAI API key as an environment variable or paste it here
openai.api_key = os.getenv("OPENAI_API_KEY") or "your-api-key-here"

def generate_image(prompt):
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024",
        response_format="b64_json"
    )
    return response.data[0]["b64_json"]

@app.route('/generate-images', methods=['POST'])
def generate_images():
    data = request.get_json()

    if not isinstance(data, list) or not data:
        return jsonify({"error": "Expected a non-empty list"}), 400

    for item in data:
        image_url = item.get("imageUrl")
        age = item.get("age")
        # You could validate and process each item here

    return jsonify({"status": "processed", "count": len(data)}), 200


    # Prompt engineering
    product_prompt = f"A pair of toddler pants on a white background, high-resolution product photo"
    lifestyle_prompt = f"A {age}-old boy running in a park wearing toddler jogger pants, realistic photography"

    try:
        product_image = generate_image(product_prompt)
        lifestyle_image = generate_image(lifestyle_prompt)

        return jsonify({
            "product_image": f"data:image/jpeg;base64,{product_image}",
            "lifestyle_image": f"data:image/jpeg;base64,{lifestyle_image}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

