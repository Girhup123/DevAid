from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter
from pygments.formatters.img import FontNotFound
import os

def code_to_image(code_text, output_file="static/output.png", font_name="Consolas", font_size=20, style="monokai"):
    folder = os.path.dirname(os.path.abspath(output_file))
    if not os.path.exists(folder):
        os.makedirs(folder)

    try:
        formatter = ImageFormatter(
            font_name=font_name,
            font_size=font_size,
            line_numbers=True,
            style=style
        )
    except FontNotFound:
        # Linux fallback
        formatter = ImageFormatter(
            font_name="DejaVu Sans Mono",
            font_size=font_size,
            line_numbers=True,
            style=style
        )

    try:
        code_bytes = highlight(code_text, PythonLexer(), formatter)
        with open(output_file, "wb") as f:
            f.write(code_bytes)
    except Exception as e:
        print(f"Error generating image: {e}")
        raise e  # this lets Flask return a 500 if something fails
