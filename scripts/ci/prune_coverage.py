import sys
import json

input_path = sys.argv[1]
output_path = sys.argv[2]

with open(input_path, 'r') as f:
    data = json.load(f)

if "files" in data:
    data["files"] = {
        k: v for k, v in data["files"].items()
        if v["summary"].get("covered_lines", 0) > 0
    }

with open(output_path, 'w') as f:
    json.dump(data, f, indent=2)

print(f"✅ Trimmed coverage.json → {output_path}")
