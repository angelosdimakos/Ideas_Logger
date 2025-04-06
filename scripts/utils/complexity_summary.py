import json
import sys

# Force stdout to UTF-8 where possible (Windows CI-safe)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

def analyze_complexity(file_path="refactor_audit.json", max_complexity=10):
    try:
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
            return run_analysis(data, max_complexity, use_emoji=True)

        except UnicodeDecodeError:
            # Retry without emojis
            with open(file_path, "r", encoding="ascii", errors="ignore") as f:
                data = json.load(f)
            return run_analysis(data, max_complexity, use_emoji=False)

    except Exception as e:
        try:
            print(f"❌ Failed to read audit file: {e}")
        except:
            print(f"[ERROR] Failed to read audit file: {e}")
        sys.exit(1)

def run_analysis(data, max_complexity, use_emoji=True):
    total_methods = 0
    warnings = []

    for file, info in data.items():
        complexity = info.get("complexity", {})
        for method, val in complexity.items():
            score = val.get("complexity") if isinstance(val, dict) else val
            if isinstance(score, (int, float)):
                total_methods += 1
                if score > max_complexity:
                    warnings.append((file, method, score))

    if use_emoji:
        print(f"\n📊 Summary:")
        print(f"🧠 Methods analyzed: {total_methods}")
        print(f"🔧 Files analyzed: {len(data)}")

        if warnings:
            print(f"\n🚨 Complexity Warnings ({len(warnings)}):")
            for file, method, score in warnings:
                print(f"⚠️ {file} → {method}: {score}")
            sys.exit(1)
        else:
            print("✅ No complexity warnings.")
    else:
        print("\n[SUMMARY]")
        print(f"Methods analyzed: {total_methods}")
        print(f"Files analyzed: {len(data)}")

        if warnings:
            print(f"\n[COMPLEXITY WARNINGS] ({len(warnings)}):")
            for file, method, score in warnings:
                print(f"[WARNING] {file} -> {method}: {score}")
            sys.exit(1)
        else:
            print("No complexity warnings.")

if __name__ == "__main__":
    analyze_complexity()
