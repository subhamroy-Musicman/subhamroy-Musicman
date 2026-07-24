import os
import json
import argparse
from datetime import datetime

LEVELS = ["#1a1a2e", "#16537e", "#1c7ed6", "#4dabf7", "#a5d8ff"]

def render_graph(input_path, output_path):
    print(f"Rendering graph to {output_path}...")
    try:
        with open(input_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {input_path}. Please run pull_contributions.py first.")
        return
        
    days = data.get("days", [])
    if not days:
        print("No contribution days found in data.")
        return
        
    # Layout constants
    cell_size = 11
    cell_gap = 4
    week_width = cell_size + cell_gap
    
    # Calculate grid dimensions based on days
    # Days are usually ordered from oldest to newest. 
    # We want them in columns of 7 (Sunday-Saturday usually, but we'll just flow them).
    
    # To keep it simple, we'll chunk them into columns of 7
    columns = []
    current_col = []
    
    # GitHub's data is sometimes sparse or doesn't perfectly align to 52 weeks depending on the year.
    # But usually it's ~365 days.
    
    for day in days:
        current_col.append(day)
        if len(current_col) == 7:
            columns.append(current_col)
            current_col = []
            
    if current_col:
        columns.append(current_col)
        
    num_cols = len(columns)
    
    width = num_cols * week_width + 40 # some padding
    height = 7 * week_width + 40 # 7 days + padding
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
    <style>
        .cell {{
            rx: 2px;
            ry: 2px;
            width: {cell_size}px;
            height: {cell_size}px;
            opacity: 0;
        }}
        @keyframes fade-in {{
            from {{ opacity: 0; transform: translateY(5px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes pulse {{
            0%, 40% {{ opacity: 1; transform: scale(1); }}
            100% {{ opacity: 0.6; transform: scale(0.95); }}
        }}
    </style>
    <g transform="translate(20, 20)">
'''

    total_commits = 0

    for col_idx, col in enumerate(columns):
        x = col_idx * week_width
        delay = col_idx * 20 # ms delay per column
        
        for row_idx, day in enumerate(col):
            y = row_idx * week_width
            level = min(max(0, day.get("level", 0)), len(LEVELS) - 1)
            color = LEVELS[level]
            if level > 0:
                total_commits += 1 # Rough proxy
                
            svg += f'        <rect class="cell" x="{x}" y="{y}" fill="{color}" style="animation: fade-in 0.5s {delay}ms forwards, pulse 2s {delay + 500}ms infinite alternate;" />\n'
            
    # Add a small legend
    legend_x = width - 120
    legend_y = height - 15
    svg += f'''
    </g>
    <g transform="translate({legend_x}, {legend_y})">
        <text x="-40" y="9" font-family="monospace" font-size="10" fill="#8b949e">Less</text>
'''
    for i, color in enumerate(LEVELS):
        svg += f'        <rect class="cell" x="{i * (cell_size + 2)}" y="0" fill="{color}" style="animation: fade-in 0.5s {num_cols * 20}ms forwards;" />\n'
        
    svg += f'''
        <text x="{(len(LEVELS) * (cell_size + 2)) + 5}" y="9" font-family="monospace" font-size="10" fill="#8b949e">More</text>
    </g>
'''

    svg += '</svg>'
    
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w") as f:
        f.write(svg)
    print(f"Saved {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render contribution graph SVG")
    parser.add_argument("input", help="Path to input JSON", nargs="?", default="assets/contributions.json")
    parser.add_argument("output", help="Path to output SVG", nargs="?", default="graph.svg")
    args = parser.parse_args()
    
    render_graph(args.input, args.output)
