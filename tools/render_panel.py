import os
import argparse

ROWS = [
    ("role", "Vibe coder, Backend coder"),
    ("stack", "JavaScript, React, Node.js, HTML, CSS, Python, C, C++, Java"),
]

def render_panel(output_path, preview=False):
    print(f"Rendering panel to {output_path}...")
    
    width = 460
    height = 250
    bg_color = "#0d1117"
    border_color = "#30363d"
    text_color = "#c9d1d9"
    label_color = "#8b949e"
    accent_color = "#4dabf7"
    
    font_family = "monospace"
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
    <style>
        .bg {{ fill: {bg_color}; stroke: {border_color}; stroke-width: 1; rx: 6px; }}
        .header {{ fill: {border_color}; }}
        .dot-red {{ fill: #ff5f56; }}
        .dot-yellow {{ fill: #ffbd2e; }}
        .dot-green {{ fill: #27c93f; }}
        .text {{ font-family: {font_family}; font-size: 14px; fill: {text_color}; }}
        .label {{ font-family: {font_family}; font-size: 14px; fill: {label_color}; font-weight: bold; }}
        .accent {{ font-family: {font_family}; font-size: 14px; fill: {accent_color}; }}
        
        @keyframes typing {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        .animated-row {{
            opacity: 0;
            animation: typing 0.1s forwards;
        }}
    </style>
    
    <!-- Window background -->
    <rect class="bg" x="1" y="1" width="{width-2}" height="{height-2}" />
    
    <!-- Window header -->
    <path class="header" d="M 1 6 Q 1 1 6 1 L {width-7} 1 Q {width-2} 1 {width-2} 6 L {width-2} 30 L 1 30 Z" />
    
    <!-- Window controls -->
    <circle class="dot-red" cx="20" cy="15" r="6" />
    <circle class="dot-yellow" cx="40" cy="15" r="6" />
    <circle class="dot-green" cx="60" cy="15" r="6" />
    
    <!-- Title -->
    <text class="label" x="{width/2}" y="20" text-anchor="middle">subhamroy-Musicman@github: ~</text>
'''

    start_y = 70
    line_height = 35
    
    for i, (label, value) in enumerate(ROWS):
        y = start_y + (i * line_height)
        delay = (i + 1) * 400 # 400ms delay per line
        
        anim_style = ""
        if not preview:
            anim_style = f"style=\"animation-delay: {delay}ms;\""
        else:
            anim_style = "style=\"opacity: 1;\""
            
        # Left-align labels, right-align values for a clean look, or just standard prompt
        svg += f'''
    <g class="animated-row" {anim_style}>
        <text class="accent" x="30" y="{y}">$</text>
        <text class="label" x="50" y="{y}">{label}</text>
        <text class="text" x="120" y="{y}">{value}</text>
    </g>
'''

    # Add cursor blinking at the end
    cursor_delay = (len(ROWS) + 1) * 400
    cursor_y = start_y + (len(ROWS) * line_height)
    if not preview:
        svg += f'''
    <g class="animated-row" style="animation-delay: {cursor_delay}ms;">
        <text class="accent" x="30" y="{cursor_y}">$</text>
        <rect class="text" x="50" y="{cursor_y-12}" width="8" height="15">
            <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite" />
        </rect>
    </g>
'''
    else:
         svg += f'''
    <g style="opacity: 1;">
        <text class="accent" x="30" y="{cursor_y}">$</text>
        <rect class="text" x="50" y="{cursor_y-12}" width="8" height="15" />
    </g>
'''

    svg += '</svg>'
    
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w") as f:
        f.write(svg)
    print(f"Saved {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render info panel SVG")
    parser.add_argument("output", help="Path to output SVG", nargs="?", default="sysinfo.svg")
    args = parser.parse_args()
    
    is_preview = os.environ.get("PREVIEW", "0") == "1"
    render_panel(args.output, preview=is_preview)
