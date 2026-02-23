import json
import re
from pathlib import Path

# Define the path to the JSON file
# Based on the context: /home/b3n/Desktop/scraped_reps/fashionbroda/fashionbroda/fashionbroda/fashionbroda/scraped_data/images_paths.json
# Adjusting to relative path assuming script is run from project root:
# fashionbroda/fashionbroda/scraped_data/images_paths.json
# Or using absolute path for safety
JSON_FILE_PATH = Path("/home/b3n/Desktop/scraped_reps/fashionbroda/fashionbroda/fashionbroda/fashionbroda/scraped_data/images_paths.json")

def clean_product_data(product_data):
    """
    Cleans the product_data dictionary values using the same logic as the spider.
    """
    if not product_data:
        return {}
    
    cleaned_data = {}
    
    for key, value in product_data.items():
        # The keys are already processed in the JSON (e.g. "price", "style_code"), 
        # so we don't need to re-clean keys typically, but we should clean the VALUES.
        
        # However, the spider logic cleaned keys from raw description. 
        # Here we are iterating over already extracted keys. 
        # We will assume keys are fine or just clean values.
        # But wait, we might want to re-apply logic if the JSON has raw-ish data?
        # The user's request is to apply the logic:
        # "if they are empty return none, just like i have in the sizes key field"
        
        clean_key = key # Key is already a string in JSON
        clean_value = value # Value from JSON
        
        # In the spider, value comes from raw string splitting. 
        # In JSON, it might already be int (price) or string.
        
        # Handle Price (Ensure int if possible, though JSON might already have int)
        if clean_key == "price":
            if isinstance(clean_value, str):
                numeric_string = "".join(
                    character for character in clean_value if character.isdigit()
                )
                try:
                    clean_value = int(numeric_string)
                except ValueError:
                    pass # Keep as is
            # If it's already int, do nothing
            
        # Handle Sizes
        if clean_key in ("sizes", "size") and isinstance(clean_value, str):
            clean_value = [
                s for s in re.split(r"[,\-/\s]+", clean_value.strip()) if s
            ]
            
        # Unified Empty Check
        if clean_value == "" or clean_value == []:
            clean_value = None
            
        cleaned_data[clean_key] = clean_value
        
    return cleaned_data

def main():
    if not JSON_FILE_PATH.exists():
        print(f"Error: File not found at {JSON_FILE_PATH}")
        return

    print(f"Reading {JSON_FILE_PATH}...")
    try:
        with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return

    print(f"Processing {len(data)} items...")
    
    processed_count = 0
    for item in data:
        if "product_data" in item:
            original_data = item["product_data"]
            item["product_data"] = clean_product_data(original_data)
            processed_count += 1
            
    print("Saving cleaned data...")
    try:
        with open(JSON_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Successfully updated {processed_count} items in {JSON_FILE_PATH}")
    except Exception as e:
        print(f"Error saving JSON: {e}")

if __name__ == "__main__":
    main()
