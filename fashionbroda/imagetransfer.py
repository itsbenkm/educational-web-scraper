# this script handles getting the images ready for upload to r2 by moving the images from the scraped_data directory to the upload_ready directory,
# and renaming the images to match the album hash, which is extracted from the images_path field in the JSON data.
# This is done to ensure that the images are named consistently and can be easily matched with their corresponding albums when uploaded to R2.

# import modules
import json
import os
from pathlib import Path

# Define the path to the JSON file containing the image paths and album hashes
images_dir = Path(
    "/home/b3n/Desktop/scraped_reps/fashionbroda/fashionbroda/fashionbroda/fashionbroda/scraped_data/images"
)
# define the json file path that contains the slug and category information for each product, which will be used to create the directory structure for the images in the upload_ready directory.
#  The JSON file is expected to have a list of products, where each product has a "category" and "slug" field that will be used to organize the images into folders based on their category and slug.
# This organization helps maintain a clear structure for the images when they are uploaded to R2, making it easier to manage and access them later on.
json_file_path = Path(
    "/home/b3n/Desktop/scraped_reps/fashionbroda/fashionbroda/fashionbroda/fashionbroda/scraped_data/slug.json"
)
# define the final destination directory for the images that are ready to be uploaded to r2
upload_ready_dir = Path(
    "/home/b3n/Desktop/scraped_reps/fashionbroda/fashionbroda/image_uploads"
)


# define the function to link the images to the upload_ready directory
def build_upload_ready():
    with open(json_file_path, "r", encoding="utf-8") as f:
        products = json.load(f)

    # get the slug and category for each product
    for product in products:

        brand = product.get("category", "").strip().lower().replace(" ", "-")
        if not brand:
            continue

        slug = product.get("slug", "").strip().lower().replace(" ", "-")
        if not slug:
            continue

        # Create folders for product images and size chart images based on the category and slug of each product. The directory structure will be organized as follows:
        # upload_ready/
        # └── brand/
        #     └── slug/
        #         ├── product/
        #         └── size-chart/
        # This structure allows for easy organization and retrieval of images based on their associated product category and
        product_dir = upload_ready_dir / brand / slug / "product"
        size_dir = upload_ready_dir / brand / slug / "size-chart"

        # create the directories if they do not exist, using the mkdir method with parents=True to create any necessary parent directories
        # and exist_ok=True to avoid raising an error if the directory already exists.
        # This ensures that the directory structure is properly set up for each product before linking the images.
        product_dir.mkdir(parents=True, exist_ok=True)
        size_dir.mkdir(parents=True, exist_ok=True)

        # now using os.link to create hard links for the images from the scraped_data directory to the upload_ready directory.
        # This method is efficient because it does not create duplicate copies of the files, but rather creates a new reference to the same file on disk.
        #  The images are renamed according to their index in the list of product images and size chart images, ensuring that they are organized and easily identifiable in the upload_ready directory.
        # This process prepares the images for upload to R2 while maintaining an organized structure based on the product category and slug.
        for index, rel_path in enumerate(
            # if the product_images_paths field is empty, it will default to an empty list, which prevents errors when trying to iterate over it.
            # then start counting the index from 1 for better readability of the image names (e.g., 01.jpg, 02.jpg, etc.) instead of starting from 0.
            product.get("product_images_paths", []),
            start=1,
        ):
            source = images_dir / rel_path
            # the destination path for the linked image is constructed using the product directory,
            # and the image is renamed to match its index in the list of product images, formatted as a two-digit number (e.g., 01.jpg, 02.jpg, etc.) for better organization and readability in the upload_ready directory.
            destination = product_dir / f"{index:02}.jpg"

            # check if the source image exists before attempting to create a hard link. If the source image does not exist, it will skip the linking process for that image,
            # which helps prevent errors and ensures that only existing images are linked to the upload_ready directory.
            # also check if the destination file exists, if it exists, it will skip the linking process for that image to avoid overwriting existing files in the upload_ready directory.
            # This ensures that the integrity of the existing files is maintained while preparing the new images for upload.
            if source.exists() and not destination.exists():
                os.link(source, destination)

        # link size chart images
        for index, rel_path in enumerate(
            product.get("size_chart_images_paths", []), start=1
        ):
            source = images_dir / rel_path
            destination = size_dir / f"{index:02}.jpg"

            if source.exists() and not destination.exists():
                os.link(source, destination)


# call the build_upload_ready function to execute the process of preparing the images for upload to r2.
# This function will read the JSON data, create the necessary directories, and copy the images to their respective locations in the upload_ready directory, renaming them according to the specified format.
if __name__ == "__main__":
    build_upload_ready()
