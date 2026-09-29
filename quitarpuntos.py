import os

# Start from the directory containing this script
ROOT = os.path.dirname(os.path.abspath(__file__))

# bottom-up is important: rename children before their parents
for current_dir, dirs, files in os.walk(ROOT, topdown=False):
    for dirname in dirs:
        if dirname.endswith("."):
            old_path = os.path.join(current_dir, dirname)

            # Remove trailing dots
            new_name = dirname.rstrip(".")
            new_path = os.path.join(current_dir, new_name)

            if not new_name:
                print(f"SKIP: {old_path} -> empty folder name")
                continue

            if os.path.exists(new_path):
                print(f"SKIP: {old_path} -> {new_path} already exists")
                continue

            try:
                os.rename(old_path, new_path)
                print(f"RENAMED: {old_path} -> {new_path}")
            except OSError as e:
                print(f"ERROR: {old_path}: {e}")

print("Done.")
