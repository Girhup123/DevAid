import os
import io
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter
from pygments.formatters.img import FontNotFound
from PIL import Image, ImageDraw


def create_gradient_background(width, height, start_color=(138, 43, 226), end_color=(30, 144, 255)):
    """Generates a smooth linear gradient background."""
    bg = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(bg)
    for y in range(height):
        r = int(start_color[0] + (end_color[0] - start_color[0]) * (y / height))
        g = int(start_color[1] + (end_color[1] - start_color[1]) * (y / height))
        b = int(start_color[2] + (end_color[2] - start_color[2]) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return bg


def code_to_image(code_text, output_file="static/output.png",
                  font_name="DejaVu Sans Mono",
                  font_size=20,
                  style="monokai",
                  padding=50,
                  window_titlebar_height=35,
                  gradient_theme="purple_blue"):

    output_file = os.path.abspath(output_file)
    folder = os.path.dirname(output_file)

    if not os.path.exists(folder):
        os.makedirs(folder)

    # 1. Initialize Pygments Formatter
    try:
        formatter = ImageFormatter(
            font_name=font_name,
            font_size=font_size,
            line_numbers=True,
            style=style,
            image_pad=15  # Internal padding inside code box
        )
    except FontNotFound:
        formatter = ImageFormatter(
            font_name="Liberation Mono",
            font_size=font_size,
            line_numbers=True,
            style=style,
            image_pad=15
        )

    # 2. Generate raw code image in-memory
    code_bytes = highlight(code_text, PythonLexer(), formatter)
    code_img = Image.open(io.BytesIO(code_bytes)).convert("RGBA")

    # 3. Calculate Dimensions with Window Header & Canvas Padding
    code_w, code_h = code_img.size
    window_w = code_w
    window_h = code_h + window_titlebar_height

    canvas_w = window_w + (padding * 2)
    canvas_h = window_h + (padding * 2)

    # 4. Define Gradient Color Presets
    gradients = {
        "purple_blue": ((138, 43, 226), (30, 144, 255)),
        "sunset": ((255, 94, 77), (255, 160, 0)),
        "cyberpunk": ((241, 7, 160), (0, 255, 240)),
        "dark": ((35, 37, 38), (65, 67, 69))
    }
    start_col, end_col = gradients.get(gradient_theme, gradients["purple_blue"])

    # 5. Create Background & Draw Window Box
    canvas = create_gradient_background(canvas_w, canvas_h, start_col, end_col)
    draw = ImageDraw.Draw(canvas)

    # Coordinates for the main window box
    win_x1 = padding
    win_y1 = padding
    win_x2 = padding + window_w
    win_y2 = padding + window_h

    # Extract dark background color from top-left pixel of Pygments output to match code theme
    bg_color = code_img.getpixel((0, 0))

    # Draw Mac Window Background + Rounded Corners
    draw.rounded_rectangle([win_x1, win_y1, win_x2, win_y2], radius=10, fill=bg_color)

    # 6. Draw macOS Red/Yellow/Green Traffic Light Buttons
    dot_y = win_y1 + (window_titlebar_height // 2)
    dots = [
        (win_x1 + 18, (255, 95, 86)),   # Red
        (win_x1 + 34, (255, 189, 46)),  # Yellow
        (win_x1 + 50, (39, 201, 63))    # Green
    ]

    for dot_x, dot_color in dots:
        draw.ellipse([dot_x - 5, dot_y - 5, dot_x + 5, dot_y + 5], fill=dot_color)

    # 7. Paste Pygments Code Image onto Canvas
    code_x = win_x1
    code_y = win_y1 + window_titlebar_height
    canvas.paste(code_img, (code_x, code_y), code_img)

    # 8. Save Final Image
    canvas.save(output_file, "PNG")
    return output_file