import os
from flask import Flask, render_template, request, jsonify, send_file
from generate import code_to_image  # make sure this file exists and works

app = Flask(__name__)

# Sample code to show on homepage
SAMPLE_CODE = """# Python sample: greeting multiple users
def greet(name):
    print(f"Hello, {name}!")

users = ["Alice", "Bob", "Charlie"]

for user in users:
    greet(user)
"""

# Home page
@app.route("/")
def home():
    return render_template("index.html", code=SAMPLE_CODE, theme="monokai", font_size=20)

# Generate image from code
@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    code = data.get("code", SAMPLE_CODE)
    theme = data.get("theme", "monokai")
    font_size = int(data.get("font_size", 20))

    # Generate the image
    code_to_image(code, "static/output.png", font_size=font_size, style=theme)
    return jsonify({"success": True, "image_url": "/static/output.png"})

# Download generated image
@app.route("/download")
def download():
    return send_file("static/output.png", as_attachment=True)

# Health check endpoint for uptime monitors
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

# Start server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render sets PORT automatically
    app.run(host="0.0.0.0", port=port)
