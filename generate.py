import os
import re
from PIL import Image, ImageDraw, ImageFont
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer, TextLexer
from pygments.styles import get_style_by_name

SUPPORTED_LANGUAGES = {
    'python': ['python', 'py'],
    'javascript': ['javascript', 'js'],
    'typescript': ['typescript', 'ts'],
    'html': ['html', 'htm'],
    'css': ['css'],
    'json': ['json'],
    'c': ['c'],
    'cpp': ['cpp', 'c++'],
    'csharp': ['csharp', 'cs'],
    'java': ['java'],
    'kotlin': ['kotlin', 'kt'],
    'swift': ['swift'],
    'go': ['go', 'golang'],
    'rust': ['rust', 'rs'],
    'php': ['php'],
    'ruby': ['ruby', 'rb'],
    'sql': ['sql'],
    'bash': ['bash', 'sh', 'zsh'],
    'yaml': ['yaml', 'yml'],
    'markdown': ['markdown', 'md'],
    'xml': ['xml']
}

GRADIENTS = {
    'purple_blue': [(138, 43, 226), (30, 144, 255)],
    'sunset': [(255, 94, 77), (255, 160, 0)],
    'cyberpunk': [(255, 0, 128), (0, 229, 255)],
    'ocean': [(15, 32, 67), (44, 83, 100)],
    'emerald': [(16, 185, 129), (5, 150, 105)],
    'dark': [(30, 30, 30), (15, 15, 15)],
    'glass_purple': [(88, 28, 135), (15, 23, 42)],
    'transparent': None
}

LIGHT_THEMES = {
    'default', 'github-light', 'vs', 'xcode', 'solarized-light', 
    'manni', 'pastie', 'friendly', 'trac', 'autumn'
}

def hex_to_rgb(hex_str, default=(248, 248, 242)):
    """Converts hex strings (#RRGGBB or #RGB) to RGB tuples."""
    if not hex_str:
        return default
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join([c * 2 for c in hex_str])
    if len(hex_str) == 6:
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    return default

def blend_colors(color, bg_color, factor=0.4):
    """Blends a color towards the background color to achieve dimming without alpha transparency."""
    return tuple(int(c * factor + bg * (1.0 - factor)) for c, bg in zip(color, bg_color))

def get_scalable_font(font_size):
    """Finds a scalable TTF font on Windows, macOS, or Linux."""
    candidates = [
        "DejaVuSansMono.ttf",
        "Consolas.ttf",
        "Courier New.ttf",
        "LiberationMono-Regular.ttf",
        "arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "C:\\Windows\\Fonts\\consola.ttf",
        "/System/Library/Fonts/Monaco.ttf"
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, font_size)
        except IOError:
            continue
    return ImageFont.load_default()

def create_gradient_background(width, height, colors):
    """Generates linear gradient canvas."""
    if not colors:
        return Image.new("RGBA", (width, height), (0, 0, 0, 0))

    base = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(base)
    c1, c2 = colors

    for y in range(height):
        ratio = y / max(height - 1, 1)
        r = int(c1[0] + (c2[0] - c1[0]) * ratio)
        g = int(c1[1] + (c2[1] - c1[1]) * ratio)
        b = int(c1[2] + (c2[2] - c1[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    return base.convert("RGBA")

def parse_line_highlights(highlight_str):
    """Parses highlight strings like '1, 3-5' into line indices."""
    highlighted = set()
    if not highlight_str:
        return highlighted

    for part in highlight_str.split(','):
        part = part.strip()
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                highlighted.update(range(start, end + 1))
            except ValueError:
                continue
        elif part.isdigit():
            highlighted.add(int(part))

    return highlighted

def code_to_image(
    code_text,
    output_file="static/exports/output.png",
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
):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    font = get_scalable_font(font_size)
    lines = code_text.splitlines() or [""]
    num_lines = len(lines)
    highlighted_set = parse_line_highlights(highlight_lines)

    # 1. Lexer Selection
    try:
        lexer = get_lexer_by_name(language)
    except Exception:
        try:
            lexer = guess_lexer(code_text)
        except Exception:
            lexer = TextLexer()

    # 2. Syntax Style Selection
    try:
        style_cls = get_style_by_name(style)
    except Exception:
        style_cls = get_style_by_name("dracula")

    tokens = list(lexer.get_tokens(code_text))

    # Dynamic Theme Colors
    is_light = style in LIGHT_THEMES or getattr(style_cls, 'background_color', '#000000').lower() in ('#ffffff', '#fff', '#f8f8f8', '#fafafa')
    
    bg_hex = getattr(style_cls, 'background_color', '#1e1e2e' if not is_light else '#ffffff')
    main_bg_rgb = hex_to_rgb(bg_hex, default=(30, 30, 46) if not is_light else (255, 255, 255))
    
    if is_light:
        header_bg = tuple(max(0, c - 18) for c in main_bg_rgb)
        footer_bg = tuple(max(0, c - 22) for c in main_bg_rgb)
        highlight_line_bg = tuple(max(0, c - 15) for c in main_bg_rgb)
        line_num_color = (130, 135, 145)
        title_color = (60, 65, 75)
        watermark_color = (80, 85, 95)
        border_color = (0, 0, 0, 40)
        separator_col = tuple(max(0, c - 30) for c in main_bg_rgb)
    else:
        header_bg = tuple(max(0, c - 12) for c in main_bg_rgb)
        footer_bg = tuple(max(0, c - 16) for c in main_bg_rgb)
        highlight_line_bg = tuple(min(255, c + 25) for c in main_bg_rgb)
        line_num_color = (110, 115, 135)
        title_color = (210, 215, 225)
        watermark_color = (190, 195, 205)
        border_color = (255, 255, 255, 35)
        separator_col = tuple(max(0, c - 8) for c in main_bg_rgb)

    # 3. Canvas & Geometry Metrics
    dummy_img = Image.new("RGB", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)

    sample_bbox = dummy_draw.textbbox((0, 0), "Agyjp", font=font)
    line_height = int((sample_bbox[3] - sample_bbox[1]) * 1.5)

    line_num_width = 0
    if show_line_numbers:
        max_num_str = str(num_lines) + "  "
        line_num_width = int(dummy_draw.textlength(max_num_str, font=font))

    max_line_width = max([dummy_draw.textlength(line, font=font) for line in lines] or [100])

    header_height = 42 if window_style in ("mac", "win") else 16
    footer_height = 45 if watermark.strip() else 15

    code_width = int(max_line_width + line_num_width + 40)
    code_height = int(num_lines * line_height + 20)

    window_width = max(code_width, 320)
    window_height = header_height + code_height + footer_height

    total_width = window_width + (padding * 2)
    total_height = window_height + (padding * 2)

    if aspect_ratio == "1:1":
        side = max(total_width, total_height)
        total_width, total_height = side, side
    elif aspect_ratio == "16:9":
        target_w = max(total_width, int(total_height * (16 / 9)))
        target_h = int(target_w * (9 / 16))
        total_width, total_height = target_w, target_h

    canvas = create_gradient_background(
        total_width, 
        total_height, 
        GRADIENTS.get(gradient_theme, GRADIENTS['purple_blue'])
    )

    # 4. Completely Opaque Window Image
    window_x = (total_width - window_width) // 2
    window_y = (total_height - window_height) // 2

    content_img = Image.new("RGB", (window_width, window_height), main_bg_rgb)
    win_draw = ImageDraw.Draw(content_img)

    # Header Bar
    if window_style in ("mac", "win"):
        win_draw.rectangle([0, 0, window_width, header_height], fill=header_bg)
        win_draw.line([(0, header_height), (window_width, header_height)], fill=separator_col, width=1)

    # Controls
    if window_style == "mac":
        dots = [(20, 21, (255, 95, 86)), (36, 21, (255, 189, 46)), (52, 21, (39, 201, 63))]
        for cx, cy, color in dots:
            win_draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=color)
    elif window_style == "win":
        ctrl_col = (120, 120, 120) if is_light else (190, 190, 210)
        win_draw.line([(window_width - 45, 16), (window_width - 35, 16)], fill=ctrl_col, width=1)
        win_draw.rectangle([window_width - 30, 13, window_width - 20, 23], outline=ctrl_col, width=1)
        win_draw.line([(window_width - 15, 13), (window_width - 5, 23)], fill=ctrl_col, width=1)
        win_draw.line([(window_width - 5, 13), (window_width - 15, 23)], fill=ctrl_col, width=1)

    if window_title and window_style != "none":
        title_bbox = win_draw.textbbox((0, 0), window_title, font=font)
        title_w = title_bbox[2] - title_bbox[0]
        win_draw.text(((window_width - title_w) // 2, 13), window_title, fill=title_color, font=font)

    # 5. Line Highlights & Numbers
    start_y = header_height + 12
    for idx in range(1, num_lines + 1):
        curr_y = start_y + (idx - 1) * line_height
        
        # Draw background bar for highlighted lines
        if highlighted_set and idx in highlighted_set:
            win_draw.rectangle(
                [0, curr_y - 2, window_width, curr_y + line_height - 2], 
                fill=highlight_line_bg
            )

        if show_line_numbers:
            num_col = line_num_color
            if highlighted_set and idx not in highlighted_set:
                num_col = blend_colors(line_num_color, main_bg_rgb, factor=0.35)
            win_draw.text((20, curr_y), f"{idx:>2} ", fill=num_col, font=font)

    # 6. Syntax Token Rendering with Opaque Color Blending
    curr_line = 1
    curr_x = 20 + line_num_width
    default_text_color = (40, 40, 40) if is_light else (248, 248, 242)

    for ttype, value in tokens:
        token_style = style_cls.style_for_token(ttype)
        color_hex = token_style.get('color')
        base_color = hex_to_rgb(f"#{color_hex}", default=default_text_color) if color_hex else default_text_color

        token_lines = value.split('\n')
        for i, token_segment in enumerate(token_lines):
            if i > 0:
                curr_line += 1
                curr_x = 20 + line_num_width

            if token_segment:
                curr_y = start_y + (curr_line - 1) * line_height
                
                # Math blending: if focus mode is active, dim unselected lines into background
                if highlighted_set and curr_line not in highlighted_set:
                    color = blend_colors(base_color, main_bg_rgb, factor=0.35)
                else:
                    color = base_color

                win_draw.text((curr_x, curr_y), token_segment, fill=color, font=font)
                curr_x += win_draw.textlength(token_segment, font=font)

    # 7. Watermark Footer Bar
    if watermark.strip():
        footer_top = window_height - footer_height
        win_draw.rectangle([0, footer_top, window_width, window_height], fill=footer_bg)
        win_draw.line([(0, footer_top), (window_width, footer_top)], fill=separator_col, width=1)

        wm_font = get_scalable_font(max(14, int(font_size * 0.85)))
        watermark_text = str(watermark).strip()
        win_draw.text((20, footer_top + 12), watermark_text, fill=watermark_color, font=wm_font)

    # Smooth Rounded Corners Mask
    mask = Image.new("L", (window_width, window_height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, window_width - 1, window_height - 1], radius=16, fill=255)

    window_img = Image.new("RGBA", (window_width, window_height), (0, 0, 0, 0))
    window_img.paste(content_img.convert("RGBA"), (0, 0), mask=mask)

    # Outer Border Line
    border_draw = ImageDraw.Draw(window_img)
    border_draw.rounded_rectangle([0, 0, window_width - 1, window_height - 1], radius=16, outline=border_color, width=1)

    canvas.alpha_composite(window_img, (window_x, window_y))
    canvas.save(output_file, "PNG")
    return output_file