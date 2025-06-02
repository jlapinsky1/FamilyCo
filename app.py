from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Set your OpenAI API key as an environment variable or paste it here
openai.api_key = os.getenv("OPENAI_API_KEY") or "your-api-key-here"

def generate_image(prompt):
    print(f"Generating image with prompt: {prompt}")  # Log the prompt
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

    # Accept a list or a single object and normalize to list
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list) or not data:
        return jsonify({"error": "Expected a non-empty list or object"}), 400

    item = data[0]  # Handle only first item for now
    image_url = item.get("imageUrl")
    age = item.get("age")
    product = item.get("product", "toddler pants")
    style = item.get("style", "")

    if not image_url or not age:
        return jsonify({"error": "Missing 'imageUrl' or 'age'"}), 400

    # Prompt cleanup
    formatted_age = age.replace("Months", "month-old").replace("Years", "year-old")
    style_desc = style.replace("_", " ").replace("-", " ").strip()

    # Prompt engineering
    product_prompt = "A pair of toddler jogger pants on a white background, catalog product photo"
    lifestyle_prompt = "A pair of toddler jogger pants displayed on a kid-sized mannequin outdoors, realistic photography"

        
    
    print("Product prompt:", product_prompt)
    print("Lifestyle prompt:", lifestyle_prompt)

    try:
        product_image = generate_image(product_prompt)
        lifestyle_image = generate_image(lifestyle_prompt)

        return jsonify({
            "product_image": f"data:image/jpeg;base64,{product_image}",
            "lifestyle_image": f"data:image/jpeg;base64,{lifestyle_image}"
        })

    except Exception as e:
        print("Image generation failed:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
