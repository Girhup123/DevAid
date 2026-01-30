import os
from flask import Flask, render_template, request, jsonify, send_file

from generate import code_to_image

app = Flask(__name__, static_folder="static", static_url_path="/static")
os.makedirs("static", exist_ok=True)

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

    code_to_image(code, "static/output.png", font_size=font_size, style=theme)

    return jsonify({"success": True, "image_url": "/static/output.png"})

# -------------------- DOWNLOAD IMAGE --------------------
@app.route("/download")
def download():
    return send_file("static/output.png", as_attachment=True)

# -------------------- HEALTH CHECK --------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

# -------------------- TOOLS ROUTE (Generic) --------------------
@app.route("/tools/<tool_name>/")
def serve_tool(tool_name):
    """
    Serve any tool located in static/tools/<tool_name>/index.html
    Example:
      /tools/error-finder/ → static/tools/error-finder/index.html
    """
    return app.send_static_file(f"tools/{tool_name}/index.html")

# -------------------- RUN APP --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

