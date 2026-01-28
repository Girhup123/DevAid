from flask import Flask, render_template, request, jsonify, send_file
from generate import code_to_image

app = Flask(__name__)

SAMPLE_CODE = """# Python sample: greeting multiple users
def greet(name):
    print(f"Hello, {name}!")

users = ["Alice", "Bob", "Charlie"]

for user in users:
    greet(user)
"""

@app.route("/")
def home():
    return render_template("index.html", code=SAMPLE_CODE, theme="monokai", font_size=20)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    code = data.get("code", SAMPLE_CODE)
    theme = data.get("theme", "monokai")
    font_size = int(data.get("font_size", 20))

    code_to_image(code, "static/output.png", font_size=font_size, style=theme)
    return jsonify({"success": True, "image_url": "/static/output.png"})

@app.route("/download")
def download():
    return send_file("static/output.png", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
