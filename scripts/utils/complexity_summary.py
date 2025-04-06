import json

def analyze_complexity(file_path="refactor_audit.json", max_complexity=10):
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to read audit file: {e}")
        exit(1)

    total_methods = 0
    warnings = []

    for file, info in data.items():
        complexity = info.get("complexity", {})
        for method, val in complexity.items():
            score = val.get("complexity") if isinstance(val, dict) else val
            if isinstance(score, (int, float)):
                total_methods += 1
                if score > max_complexity:
                    warnings.append(f"⚠️ {file} → {method}: {score}")

    print(f"\n📊 Summary:")
    print(f"🧠 Methods analyzed: {total_methods}")
    print(f"🔧 Files analyzed: {len(data)}")

    if warnings:
        print(f"\n🚨 Complexity Warnings ({len(warnings)}):")
        for w in warnings:
            print(w)
        exit(1)  # ❌ Optional: fail the job if warnings exist
    else:
        print("✅ No complexity warnings.")

if __name__ == "__main__":
    analyze_complexity()
