import os
import uuid
import io
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
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

# -------------------- GENERATE IMAGE (WEB UI) --------------------
@app.route("/generate", methods=["POST"])
def generate():
    data = request.json or {}
    code = data.get("code", SAMPLE_CODE)
    theme = data.get("theme", "monokai")
    font_size = int(data.get("font_size", 20))
    gradient = data.get("gradient", "purple_blue")

    # Generate a unique filename using UUID
    unique_filename = f"output_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join("static", unique_filename)

    # Pass parameters to the updated generator
    code_to_image(code, filepath, font_size=font_size, style=theme, gradient_theme=gradient)

    return jsonify({"success": True, "image_url": f"/static/{unique_filename}", "filename": unique_filename})

# -------------------- REST API ENDPOINT --------------------
@app.route("/api/generate", methods=["POST"])
def api_generate():
    """
    Public REST API endpoint for developers.
    Payload (JSON):
    {
      "code": "print('hello world')",
      "theme": "monokai",
      "font_size": 20,
      "gradient": "purple_blue"
    }
    """
    try:
        data = request.get_json(force=True) or {}
        code = data.get("code", SAMPLE_CODE)
        theme = data.get("theme", "monokai")
        font_size = int(data.get("font_size", 20))
        gradient = data.get("gradient", "purple_blue")

        # Create temporary file to hold the rendered image
        temp_filename = f"api_{uuid.uuid4().hex[:8]}.png"
        temp_path = os.path.join("static", temp_filename)

        code_to_image(code, temp_path, font_size=font_size, style=theme, gradient_theme=gradient)

        # Read into memory buffer so we can delete temp file or stream directly
        with open(temp_path, "rb") as f:
            image_buffer = io.BytesIO(f.read())
        
        # Cleanup temporary API file from disk
        if os.path.exists(temp_path):
            os.remove(temp_path)

        image_buffer.seek(0)
        return send_file(
            image_buffer,
            mimetype="image/png",
            as_attachment=False,
            download_name="code.png"
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

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