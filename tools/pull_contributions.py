import os
import json
import argparse
import urllib.request
import re
import datetime
import random

def pull_contributions(username, output_path):
    print(f"Fetching contributions for {username}...")
    url = f"https://github.com/users/{username}/contributions"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
    except Exception as e:
        print(f"Failed to fetch contributions: {e}")
        create_dummy_data(output_path)
        return
        
    days = []
    
    tag_pattern = re.compile(r'<[^>]+data-date="([^"]+)"[^>]+data-level="([^"]+)"[^>]*>')
    matches = tag_pattern.findall(html)
    if matches:
        days = [{"date": m[0], "level": int(m[1])} for m in matches]
    else:
        tag_pattern_rev = re.compile(r'<[^>]+data-level="([^"]+)"[^>]+data-date="([^"]+)"[^>]*>')
        matches = tag_pattern_rev.findall(html)
        if matches:
            days = [{"date": m[1], "level": int(m[0])} for m in matches]

    # Clean up duplicates
    unique_days = {}
    for day in days:
        unique_days[day["date"]] = day
        
    days = list(unique_days.values())
    
    # Sort by date
    days.sort(key=lambda x: x["date"])
    
    if not days:
        print("Warning: Could not parse any contribution days. GitHub markup might have changed.")
        create_dummy_data(output_path)
        return
        
    data = {
        "username": username,
        "total_days": len(days),
        "days": days
    }
    
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"Saved {len(days)} days of contributions to {output_path}")

def create_dummy_data(output_path):
    print("Generating dummy contribution data...")
    days = []
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=365)
    
    curr_date = start_date
    while curr_date <= end_date:
        level = random.choices([0, 1, 2, 3, 4], weights=[0.6, 0.15, 0.1, 0.1, 0.05])[0]
        days.append({
            "date": curr_date.strftime("%Y-%m-%d"),
            "level": level
        })
        curr_date += datetime.timedelta(days=1)
        
    data = {
        "username": "dummyuser",
        "total_days": len(days),
        "days": days
    }
    
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pull GitHub contributions")
    parser.add_argument("username", help="GitHub username", nargs="?", default="dummyuser")
    parser.add_argument("output", help="Path to output JSON", nargs="?", default="assets/contributions.json")
    args = parser.parse_args()
    
    pull_contributions(args.username, args.output)
