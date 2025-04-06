import json
import sys

def analyze_complexity(file_path="refactor_audit.json", max_complexity=10):
    try:
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
        except UnicodeDecodeError:
            print("⚠️ UTF-8 decoding failed. Retrying without emojis...")
            with open(file_path, "r", encoding="ascii", errors="ignore") as f:
                data = json.load(f)
            return analyze_complexity_no_emoji(data, max_complexity)

        return analyze_complexity_with_emoji(data, max_complexity)

    except Exception as e:
        print(f"❌ Failed to read audit file: {e}")
        sys.exit(1)

def analyze_complexity_with_emoji(data, max_complexity):
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
        sys.exit(1)
    else:
        print("✅ No complexity warnings.")

def analyze_complexity_no_emoji(data, max_complexity):
    total_methods = 0
    warnings = []

    for file, info in data.items():
        complexity = info.get("complexity", {})
        for method, val in complexity.items():
            score = val.get("complexity") if isinstance(val, dict) else val
            if isinstance(score, (int, float)):
                total_methods += 1
                if score > max_complexity:
                    warnings.append(f"[WARNING] {file} -> {method}: {score}")

    print(f"\n[SUMMARY]")
    print(f"Methods analyzed: {total_methods}")
    print(f"Files analyzed: {len(data)}")

    if warnings:
        print(f"\n[COMPLEXITY WARNINGS] ({len(warnings)}):")
        for w in warnings:
            print(w)
        sys.exit(1)
    else:
        print("No complexity warnings.")

if __name__ == "__main__":
    analyze_complexity()
