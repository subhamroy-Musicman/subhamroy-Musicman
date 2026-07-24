import os
import argparse
from PIL import Image

# left = light/empty, right = dense/dark
GLYPHS = " '.,:;~+*xXO#"

def render_portrait(input_path, output_path, cols=60, font_width=7, font_height=14):
    print(f"Rendering {input_path} to {output_path}...")
    try:
        img = Image.open(input_path).convert("L")
    except FileNotFoundError:
        print(f"Error: Could not find {input_path}. Please run clean_photo.py first.")
        return
        
    # Calculate target dimensions
    W, H = img.size
    ratio = H / W
    rows = int(cols * ratio * (font_width / font_height))
    
    img = img.resize((cols, rows), Image.Resampling.LANCZOS)
    pixels = img.load()
    
    # Generate ASCII text
    ascii_rows = []
    for y in range(rows):
        row = ""
        for x in range(cols):
            # Invert brightness: 255 (white) -> index 0 (space), 0 (black) -> index max (darkest glyph)
            brightness = pixels[x, y]
            # normalized 0.0 to 1.0 (where 0.0 is white, 1.0 is black)
            val = 1.0 - (brightness / 255.0)
            
            idx = int(val * (len(GLYPHS) - 1))
            idx = max(0, min(len(GLYPHS) - 1, idx))
            
            # replace space with non-breaking space for svg
            char = GLYPHS[idx]
            if char == " ":
                char = "&#160;"
            # Escape HTML characters
            elif char == "&": char = "&amp;"
            elif char == "<": char = "&lt;"
            elif char == ">": char = "&gt;"
                
            row += char
        ascii_rows.append(row)
        
    svg_width = cols * font_width
    svg_height = rows * font_height
    accent_color = "#4dabf7" # From the levels later
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">
    <style>
        .text {{
            font-family: monospace;
            font-size: {font_height}px;
            white-space: pre;
            fill: {accent_color};
        }}
        @keyframes reveal {{
            0% {{ clip-path: inset(0 100% 0 0); }}
            100% {{ clip-path: inset(0 0 0 0); }}
        }}
    </style>
'''
    
    for i, row in enumerate(ascii_rows):
        y_pos = (i + 1) * font_height
        delay = i * 40 # ms
        duration = 500 # ms
        
        # SVG clipPath inside the SVG directly using embedded styling
        clip_id = f"clip-{i}"
        
        # Using a style directly on the text element for the animation
        # clip-path: polygon for standard SVG reveal
        svg += f'''
    <g style="animation: reveal {duration}ms {delay}ms both;">
        <text x="0" y="{y_pos}" class="text">{row}</text>
    </g>'''

    svg += '\n</svg>'
    
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w") as f:
        f.write(svg)
    print(f"Saved {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render ASCII portrait SVG")
    parser.add_argument("input", help="Path to input photo", nargs="?", default="assets/photo-ready.png")
    parser.add_argument("output", help="Path to output SVG", nargs="?", default="portrait.svg")
    args = parser.parse_args()
    
    render_portrait(args.input, args.output)
