import json
import sys
import os

# Force stdout to UTF-8 where possible (Windows CI-safe)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

def analyze_complexity(file_path="refactor_audit.json", max_complexity=10):
    try:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            sys.exit(1)

        with open(file_path, "r", encoding="utf-8-sig") as f:
            content = f.read().strip()
            if not content:
                print(f"❌ Audit file is empty: {file_path}")
                sys.exit(1)
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON in audit file: {e}")
                print("\n🔎 Dumping first few lines for inspection:")
                print("\n".join(content.splitlines()[:10]))
                sys.exit(1)

        return run_analysis(data, max_complexity, use_emoji=True)


    except Exception as e:
        print(f"❌ Unexpected error: {e}")
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
            print("⚠️ Complexity warnings found, but continuing the process.")
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
