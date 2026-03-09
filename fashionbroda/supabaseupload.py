import json
from pathlib import Path

json_file_path = Path(
    "/home/b3n/Desktop/scraped_reps/fashionbroda/fashionbroda/fashionbroda/fashionbroda/scraped_data/slug.json"
)
output_path = Path(
    "/home/b3n/Desktop/scraped_reps/fashionbroda/fashionbroda/fashionbroda/fashionbroda/scraped_data/supabase.json"
)
r2_urls = Path(
    "/home/b3n/Desktop/scraped_reps/fashionbroda/fashionbroda/fashionbroda/fashionbroda/scraped_data/r2_paths.txt"
)


try:
    # Open the file in read mode with UTF-8 encoding
    with open(json_file_path, "r", encoding="utf-8") as data:
        products = json.load(data)

# account for exceptions that may occur during file reading
except FileNotFoundError:
    print(f"JSON file not found at: {json_file_path}")
    raise SystemExit("JSON file not found")
except json.JSONDecodeError as e:
    print(f"Invalid JSON format: {e}")
    raise SystemExit("Invalid JSON file")
except Exception as e:
    print(f"Unexpected error reading JSON file: {e}")
    raise SystemExit("Error reading JSON file")


# read the txt file line by line
try:
    with open(r2_urls, "r", encoding="utf-8") as r2_file:
        # read the txt file line by line, and strip any leading or trailing whitespace from each line
        r2_paths = [path.strip() for path in r2_file]
except FileNotFoundError:
    print(f"R2 paths file not found at: {r2_urls}")
    raise SystemExit("R2 paths file not found")
except Exception as e:
    print(f"Unexpected error reading R2 paths file: {e}")
    raise SystemExit("Error reading R2 paths file")


# create the full image cdn urls by concatenating the base URL with the paths from the r2_paths list, and store the resulting URLs in a new list called r2_urls.
def create_full_r2_urls(r2_paths):
    base_url = "https://cdn.reps.cheap/products/"
    product_image_urls = []
    size_chart_urls = []
    for path in r2_paths:
        full_url = base_url + path
        if "product" in path:
            product_image_urls.append(full_url)
        elif "size-chart" in path:
            size_chart_urls.append(full_url)
    return product_image_urls, size_chart_urls


# define the allowed keys from the slug.json file that we want to include in the final JSON data for Supabase,
# and create a new dictionary for each product that only includes these allowed keys and their corresponding values.
def new_product(product):
    return dict(
        category=product.get("category"),
        slug=product.get("slug"),
        # yupoo_album_url=product.get("album_url"),
        # product_data=product.get("product_data"),
    )


# create a function to match the r2 urls to the corresponding products based on their slugs, and add the matched URLs to the new product dictionary under the keys "product_image_urls" and "size_chart_image_urls".
# This function will iterate through the list of products and the list of R2 URLs, and for each product, it will check if the slug is present in any of the R2 URLs.
# If a match is found, it will add the corresponding URLs to the product's dictionary. This way, we can ensure that each product in our final JSON data has the correct image URLs associated with it for upload to Supabase.
def match_r2_urls_to_products(products, create_full_r2_urls):
    product_image_urls, size_chart_urls = create_full_r2_urls(r2_paths)
    for product in products:
        slug = product.get("slug")
        if not slug:
            continue
        matched_product_urls = [url for url in product_image_urls if slug in url]
        matched_size_chart_urls = [url for url in size_chart_urls if slug in url]
        product["product_image_urls"] = matched_product_urls
        product["size_chart_image_urls"] = matched_size_chart_urls


# Create json data to be uploaded to supabase
def create_supabase_json(products, match_r2_urls_to_products):
    match_r2_urls_to_products(products, create_full_r2_urls)
    supabase_data = []
    for product in products:
        new_prod = new_product(product)
        new_prod["is_active"] = (
            True  # Add the is_active key with a default value of True
        )
        new_prod["is_deleted"] = False
        new_prod["yupoo_album_url"] = product.get("album_url")
        new_prod["product_image_urls"] = product.get("product_image_urls")
        new_prod["size_chart_image_urls"] = product.get("size_chart_image_urls")
        new_prod["product_data"] = product.get("product_data")
        supabase_data.append(new_prod)
    return supabase_data


# create the final json data function to be called
final_supabase_json = create_supabase_json(products, match_r2_urls_to_products)


with open(output_path, "w", encoding="utf-8") as f:
    json.dump(final_supabase_json, f, indent=2)
