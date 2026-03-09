import json
from pathlib import Path

from supabase import Client, create_client

SUPABASE_DB_URL = ""
SUPABASE_SECRET_KEY = ""
SELLER_ID = "68315cdb-5674-4305-b20f-99ab05c5c526"
# connect to supabase database
"""
supabase        → the variable that holds the connection
: Client        → type hint, just tells your editor what type it is
create_client() → the function that actually creates the connection
SUPABASE_PUBLIC_KEY   → tells it where your database is
SUPABASE_SECRET_KEY → proves you're allowed to access it
"""
supabase: Client = create_client(SUPABASE_DB_URL, SUPABASE_SECRET_KEY)
json_file_path = Path(
    "/home/b3n/Desktop/scraped_reps/fashionbroda/fashionbroda/fashionbroda/fashionbroda/scraped_data/supabase.json"
)


def upload_to_supabase():
    try:
        print("📂 Reading JSON file...")
        # Open the file in read mode with UTF-8 encoding
        with open(json_file_path, "r", encoding="utf-8") as data:
            all_products = json.load(data)

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

    products = all_products
    print(f"✅ Processing {len(products)} of {len(all_products)} products\n")

    # start a counter for successful uploads
    fashionbroda_successful_uploads = 0
    product_data_successful_uploads = 0
    # start a counter for failed uploads
    fashionbroda_failed_uploads = 0
    product_data_failed_uploads = 0

    # loop throught the products and upload each one to supabase
    for product in products:
        # use a try except block to account for any errors that may occur during the upload process
        try:
            # get the product data in the format we want to upload to supabase
            fashionbroda_products = {
                "seller_id": SELLER_ID,
                "category": product.get("category"),
                "slug": product.get("slug"),
                "is_active": product.get("is_active", True),
                "is_deleted": product.get("is_deleted", False),
                "yupoo_album_url": product.get("yupoo_album_url"),
                "product_image_urls": product.get("product_image_urls", []),
                "size_chart_image_urls": product.get("size_chart_image_urls", []),
            }
            """
            # supabase.table() → tells supabase which table to work with, like "FROM fashionbroda_products" in SQL
            # .upsert() → insert if the slug doesn't exist, update if it already does — safe to re-run without duplicates
            # on_conflict="slug" → use the slug column to check for duplicates, since it is unique in the table
            # .execute() → actually fires the request to supabase, without this nothing happens
            
            """
            fashionbroda_products_response = (
                supabase.table("fashionbroda_products")
                .upsert(fashionbroda_products, on_conflict="slug")
                .execute()
            )
            # if there is no response from supabase print what failed to upload and increase the counter of the failed uploads by 1, and continue to the next product,
            if not fashionbroda_products_response.data:
                print(f"❌ Failed to upload product: {product.get('slug')}")
                fashionbroda_failed_uploads += 1
                continue
            # otherwise print what successfully uploaded and increase the counter of successful uploads by 1
            else:
                print(f"✅ Successfully uploaded product: {product.get('slug')}")
                fashionbroda_successful_uploads += 1

            # get the product_id to be used in linking to the product_data table, and print it out
            """
            product_response.data
            # → the response from supabase after the upsert
            # → contains the full row that was inserted as a list
            # → looks like this:
            # [{ "id": "abc-123", "slug": "acne-studios-...", "category": "Acne Studios", ... }]

            product_response.data[0]
            # → grabs the first item in the list (there's only one since we inserted one product)
            # → looks like this:
            # { "id": "abc-123", "slug": "acne-studios-...", "category": "Acne Studios", ... }

            product_response.data[0]["id"]
            # → grabs just the id value from that dictionary
            # → "abc-123"
            """
            product_id = fashionbroda_products_response.data[0].get("id")
            print(f"📦 Product ID: {product_id}")

            #!##########################################################################################
            # since product data is nested inside the main product dictionary, we need to get it and format it for upload to the product_data table in supabase,
            # and link it to the main product using the product_id we just got from the response after uploading to the fashionbroda_products table
            data = product.get("product_data", {})
            product_data = {
                "product_id": product_id,
                "price": data.get("price"),
                "style_code": data.get("style_code"),
                "fabric": data.get("fabric"),
                "fit": data.get("fit"),
                "sizes": data.get("sizes"),
                "features": data.get("features"),
            }
            product_data_response = (
                supabase.table("product_data")
                .upsert(product_data, on_conflict="product_id")
                .execute()
            )

            if not product_data_response.data:
                print(
                    f"❌ Failed to upload product data for product: {product.get('slug')}"
                )
                product_data_failed_uploads += 1
                continue
            else:
                print(
                    f"✅ Successfully uploaded product data for product: {product.get('slug')}"
                )
                product_data_successful_uploads += 1

        # account for any exceptions that may occur during the upload process,
        # print what failed to upload and the error message, increase the counter of failed uploads by 1, and continue to the next product
        except Exception as e:
            print(f"❌ Error uploading product: {product.get('slug')}, error: {e}")
            fashionbroda_failed_uploads += 1
            continue

    print("\n🎉 Done")
    print(f"✅ Products uploaded: {fashionbroda_successful_uploads}")
    print(f"✅ Product data uploaded: {product_data_successful_uploads}")
    print(f"❌ Products failed: {fashionbroda_failed_uploads}")
    print(f"❌ Product data failed: {product_data_failed_uploads}")


if __name__ == "__main__":
    upload_to_supabase()
