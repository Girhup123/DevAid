import os
import uuid
import urllib.parse
from flask import Flask, render_template, request, jsonify, send_file
from generate import code_to_image, SUPPORTED_LANGUAGES

app = Flask(__name__)

OUTPUT_DIR = os.path.join("static", "exports")
os.makedirs(OUTPUT_DIR, exist_ok=True)

DEFAULT_CODE = """# QuickSort Algorithm
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

numbers = [3, 6, 8, 10, 1, 2, 1]
print("Sorted array:", quicksort(numbers))"""

def parse_bool(val) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() in ('true', '1', 't', 'yes', 'on')
    return True

@app.route('/')
def index():
    code = request.args.get('code', DEFAULT_CODE)
    language = request.args.get('language', 'python')
    theme = request.args.get('theme', 'dracula')
    gradient = request.args.get('gradient', 'purple_blue')
    font_size = request.args.get('font_size', '20')
    window_title = request.args.get('window_title', 'main.py')
    window_style = request.args.get('window_style', 'mac')
    aspect_ratio = request.args.get('aspect_ratio', 'auto')
    highlight_lines = request.args.get('highlight_lines', '')
    show_line_numbers = parse_bool(request.args.get('show_line_numbers', 'true'))
    padding = request.args.get('padding', '60')
    watermark = request.args.get('watermark', '')

    languages_list = sorted(SUPPORTED_LANGUAGES.keys())

    return render_template(
        'index.html',
        code=code,
        language=language,
        theme=theme,
        gradient=gradient,
        font_size=font_size,
        window_title=window_title,
        window_style=window_style,
        aspect_ratio=aspect_ratio,
        highlight_lines=highlight_lines,
        show_line_numbers=show_line_numbers,
        padding=padding,
        watermark=watermark,
        languages=languages_list
    )

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json or {}

    code = data.get("code", DEFAULT_CODE)
    language = data.get("language", "python")
    theme = data.get("theme", "dracula")
    gradient = data.get("gradient", "purple_blue")

    try:
        font_size = int(data.get("font_size", 20))
    except (ValueError, TypeError):
        font_size = 20

    try:
        padding = int(data.get("padding", 60))
    except (ValueError, TypeError):
        padding = 60

    window_title = data.get("window_title", "main.py")
    window_style = data.get("window_style", "mac")
    aspect_ratio = data.get("aspect_ratio", "auto")
    highlight_lines = data.get("highlight_lines", "")
    show_line_numbers = parse_bool(data.get("show_line_numbers", True))
    watermark = data.get("watermark", "")

    unique_id = uuid.uuid4().hex[:8]
    filename = f"snippet_{unique_id}.png"
    output_path = os.path.join(OUTPUT_DIR, filename)

    code_to_image(
        code_text=code,
        output_file=output_path,
        language=language,
        font_size=font_size,
        style=theme,
        gradient_theme=gradient,
        window_title=window_title,
        window_style=window_style,
        aspect_ratio=aspect_ratio,
        highlight_lines=highlight_lines,
        show_line_numbers=show_line_numbers,
        padding=padding,
        watermark=watermark
    )

    params = {
        'code': code,
        'language': language,
        'theme': theme,
        'gradient': gradient,
        'font_size': font_size,
        'window_title': window_title,
        'window_style': window_style,
        'aspect_ratio': aspect_ratio,
        'highlight_lines': highlight_lines,
        'show_line_numbers': str(show_line_numbers).lower(),
        'padding': padding,
        'watermark': watermark
    }
    share_url = f"{request.host_url}?{urllib.parse.urlencode(params)}"

    return jsonify({
        "success": True,
        "image_url": f"/static/exports/{filename}",
        "filename": filename,
        "share_url": share_url
    })

@app.route('/download/<filename>')
def download(filename):
    file_path = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(file_path):
        code_to_image(
            code_text=DEFAULT_CODE,
            output_file=file_path,
            language="python",
            font_size=20,
            style="dracula",
            gradient_theme="purple_blue",
            window_title="main.py",
            window_style="mac",
            aspect_ratio="auto",
            highlight_lines="",
            show_line_numbers=True,
            padding=60,
            watermark=""
        )

    return send_file(
        file_path,
        as_attachment=True,
        download_name="devaid-code.png",
        mimetype="image/png"
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)