import os
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
from generate import code_to_image

app = Flask(__name__, static_folder="static", static_url_path="/static")
os.makedirs("static", exist_ok=True)

# -------------------- SAMPLE CODE --------------------
SAMPLE_CODE = """# Python sample: greeting multiple users
def greet(name):
    print(f"Hello, {name}!")

users = ["Alice", "Bob", "Charlie"]

for user in users:
    greet(user)
"""

# -------------------- HOME --------------------
@app.route("/")
def home():
    return render_template("index.html", code=SAMPLE_CODE, theme="monokai", font_size=20)

# -------------------- GENERATE IMAGE --------------------
@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    code = data.get("code", SAMPLE_CODE)
    theme = data.get("theme", "monokai")
    font_size = int(data.get("font_size", 20))

    # Generate a unique filename using UUID
    unique_filename = f"output_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join("static", unique_filename)

    # Pass the unique path to the renderer
    code_to_image(code, filepath, font_size=font_size, style=theme)

    return jsonify({"success": True, "image_url": f"/static/{unique_filename}", "filename": unique_filename})

# -------------------- DOWNLOAD IMAGE --------------------
@app.route("/download/<filename>")
def download(filename):
    # Securely serve the specific file as an attachment
    return send_from_directory("static", filename, as_attachment=True)

# -------------------- HEALTH CHECK --------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

# -------------------- RUN APP --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)