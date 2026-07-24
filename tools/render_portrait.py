import os
import argparse
from PIL import Image

# left = light/empty, right = dense/dark
GLYPHS = " '.,:;~+*xXO#"

def render_portrait(input_path, output_path, cols=60, font_width=7, font_height=14):
    print(f"Rendering colored portrait from {input_path} to {output_path}...")
    try:
        # Load color image
        img_color = Image.open(input_path).convert("RGB")
    except FileNotFoundError:
        print(f"Error: Could not find {input_path}. Please run clean_photo.py first.")
        return
        
    # Calculate target dimensions
    W, H = img_color.size
    ratio = H / W
    rows = int(cols * ratio * (font_width / font_height))
    
    img_color = img_color.resize((cols, rows), Image.Resampling.LANCZOS)
    pixels_color = img_color.load()
    
    img_gray = img_color.convert("L")
    pixels_gray = img_gray.load()
    
    # Generate SVG content
    svg_width = cols * font_width
    svg_height = rows * font_height
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">
    <style>
        .text {{
            font-family: monospace;
            font-size: {font_height}px;
            white-space: pre;
        }}
        @keyframes reveal {{
            0% {{ clip-path: inset(0 100% 0 0); }}
            100% {{ clip-path: inset(0 0 0 0); }}
        }}
    </style>
'''
    
    for y in range(rows):
        y_pos = (y + 1) * font_height
        delay = y * 40 # ms
        duration = 800 # ms
        
        row_html = ""
        for x in range(cols):
            # Grayscale brightness for glyph selection
            brightness = pixels_gray[x, y]
            val = 1.0 - (brightness / 255.0)
            idx = int(val * (len(GLYPHS) - 1))
            idx = max(0, min(len(GLYPHS) - 1, idx))
            
            char = GLYPHS[idx]
            if char == " ":
                char = "&#160;"
            elif char == "&": char = "&amp;"
            elif char == "<": char = "&lt;"
            elif char == ">": char = "&gt;"
            
            # Get pixel color
            r, g, b = pixels_color[x, y]
            color_hex = f"#{r:02x}{g:02x}{b:02x}"
            
            # Wrap char in tspan with color
            row_html += f'<tspan fill="{color_hex}">{char}</tspan>'
            
        svg += f'''
    <g style="animation: reveal {duration}ms {delay}ms both;">
        <text x="0" y="{y_pos}" class="text">{row_html}</text>
    </g>'''

    svg += '\n</svg>'
    
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Saved {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render ASCII portrait SVG")
    parser.add_argument("input", help="Path to input photo", nargs="?", default="assets/photo-ready.png")
    parser.add_argument("output", help="Path to output SVG", nargs="?", default="portrait.svg")
    args = parser.parse_args()
    
    render_portrait(args.input, args.output)
