import os
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter
from pygments.formatters.img import FontNotFound


def code_to_image(code_text, output_file="static/output.png",
                  font_name="DejaVu Sans Mono",
                  font_size=20,
                  style="monokai"):

    output_file = os.path.abspath(output_file)
    folder = os.path.dirname(output_file)

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
        formatter = ImageFormatter(
            font_name="Liberation Mono",
            font_size=font_size,
            line_numbers=True,
            style=style
        )

    code_bytes = highlight(code_text, PythonLexer(), formatter)

    with open(output_file, "wb") as f:
        f.write(code_bytes)
