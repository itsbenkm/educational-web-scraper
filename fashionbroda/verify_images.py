import json
from pathlib import Path

# Use the exact path confirmed by the `check_json.py` script
JSON_FILE_PATH = Path(
    "/home/b3n/Desktop/scraped_reps/fashionbroda/fashionbroda/fashionbroda/fashionbroda/scraped_data/images_paths.json"
)
# Images are stored in the same `scraped_data` folder under `images`
IMAGES_STORE = JSON_FILE_PATH.parent / "images"


def main():
    if not JSON_FILE_PATH.exists():
        print(f"Error: JSON file not found at {JSON_FILE_PATH}")
        return

    print(f"Reading {JSON_FILE_PATH}...")
    try:
        with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return

    total_items = len(data)
    total_images_checked = 0
    missing_images = []

    print(f"Verifying images for {total_items} items...")

    for item in data:
        # Check product images
        for relative_path in item.get("product_images_paths", []):
            if relative_path:
                full_path = IMAGES_STORE / relative_path
                total_images_checked += 1
                if not full_path.exists():
                    missing_images.append(str(full_path))

        # Check size chart images
        for relative_path in item.get("size_chart_images_paths", []):
            if relative_path:
                full_path = IMAGES_STORE / relative_path
                total_images_checked += 1
                if not full_path.exists():
                    missing_images.append(str(full_path))

    # Report results
    print("-" * 50)
    print(f"Total images checked: {total_images_checked}")
    print(f"Missing images found: {len(missing_images)}")

    if missing_images:
        print("-" * 50)
        print("First 10 missing files:")
        for path in missing_images[:10]:
            print(f"XX {path}")

        # Save missing paths to a file for review
        report_path = "missing_images_report.txt"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(missing_images))
        print(f"\nFull list of missing images saved to: {report_path}")
    else:
        print("\nSUCCESS: All referenced images exist on disk.")


if __name__ == "__main__":
    main()
