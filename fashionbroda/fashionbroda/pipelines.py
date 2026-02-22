# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# import hashlib to handle image downloads and to generate unique filenames (hashbased storage) for the images we scrape,
# this helps to avoid naming conflicts and ensures that each image is saved with a unique name based on its content
import hashlib

# Import Scrapy's Request class so we can manually generate image download requests
# inside get_media_requests().
#
# We need this because the default ImagesPipeline request generation is too generic
# for sites like Yupoo, which often enforce hotlink protection.
#
# By creating Request objects ourselves, we can:
# - Attach required HTTP headers (e.g. Referer)
# - Propagate item-level context via request.meta
# - Let Scrapy's downloader and retry middleware handle the actual networking
#
# NOTE:
# - This does NOT perform the download directly.
# - This does NOT override retry behavior (Scrapy still controls retries).
# - We are only customizing how image requests are constructed.
from scrapy import Request

# useful for handling different item types with a single interface
from scrapy.pipelines.images import ImagesPipeline

# import the ImageItem class from items.py to structure the scraped data

# *------------------------------------------------------------------------------------------------------------------------------------------------------


# define the ImagesPipeline class that extends Scrapy's ImagesPipeline
class ImagesPipeline(ImagesPipeline):
    # override the get_media_requests method to customize image download requests
    def get_media_requests(self, item, info):
        # set the referer header to the album URL from the item context, then add a fallback if the album_url is missing, to avoid errors
        # if the album_url is missing, set referer to an empty string
        referer = item.get("album_url", "")

        # loop through each product image URL in the item
        # we use item.get("product_images", []) to safely access the product_images field,
        #  providing an empty list as a default if the field is missing or None, this prevents errors and allows the loop to run without issues even if there are no product images in the item
        for product_image_url in item.get("product_images", []):
            # yield a Request for each image URL with the referer header set,
            yield Request(
                # the URL of the image to download, this is the product image URL from the item context
                url=product_image_url,
                # set the referer header to the album URL from the item context, this is important for servers that require a referer to allow access to the image
                headers={"Referer": referer},
                # meta propagation of the info that is in the images.json file and that was defined in the ImageDownloadItem
                # This metadata allows custom file paths or post-processing logic if needed
                meta={"item": item, "image_type": "product_image"},
                # this line : 'image_type': 'product_image'
                # allows us to differentiate between product images and size chart images later, so we can store them in different fields
            )

        # loop through each size chart image URL in the item
        for size_chart_url in item.get("size_chart_images", []):
            # yield a Request for each size chart image URL with the referer header set
            yield Request(
                # the URL of the image to download, this is the size chart image URL from the item context
                url=size_chart_url,
                # set the referer header to the album URL from the item context, this is important for servers that require a referer to allow access to the image
                headers={"Referer": referer},
                # meta propagation of contextual data already attached to the item
                meta={"item": item, "image_type": "size_chart_image"},
                # this line : 'image_type': 'size_chart_image'
                # allows us to differentiate between product images and size chart images later, so we can store them in different fields
            )

    # *-------------------------------------------------------------------------------------------------------------------------------------------------

    def normalize_category(self, value):
        """
        Normalize a controlled category string into a filesystem-safe form.
        Assumes value comes from a predefined vocabulary.
        """
        if not value:
            return "unknown_category"

        return value.lower().strip().replace(" ", "_")

        # *-------------------------------------------------------------------------------------------------------------------------------------------------

        # define the function to determine the file paths of the downloaded images
        # we will be using hash based file naming to ensure unique and consistent file names for the images
        # this helps in avoiding duplicate downloads and makes it easier to manage the images in storage
        # scrapy will call this function for each image being downloaded, and will use the returned path to save the image

        """Determine the file path for each downloaded image using hash-based naming.

        This method generates a unique file name for each image based on its URL.
        It uses SHA1 hashing to create a consistent and collision-resistant name.
        The images are organized into subdirectories based on their type
        (product images vs. size chart images) for better manageability.

        Args:
            request (Request): The Scrapy Request object for the image download.
            response (Response, optional): The HTTP response object (not used here).
            info (PipelineInfo, optional): Pipeline information (not used here).
            item (Item, optional): The scraped item containing metadata.
        Returns:
            str: The file path where the image will be stored.
        """

        """
        
        file_path() determines WHERE on disk each downloaded image will be stored.
        Scrapy calls this method AFTER an image is successfully downloaded.
        The returned string must be a RELATIVE file path (inside IMAGES_STORE).
        
        Parameters:
        - request:
            The Request object that downloaded the image.
            This is the most important argument because it contains:
            request.url        → the image URL
            request.meta       → custom metadata we attached earlier
                (e.g. item context, image_type, seller, album info)

        - response (optional):
            The Response object for the downloaded image.
            Often unused for naming, but provided by Scrapy for advanced cases.

        - info (optional):
            Internal Scrapy pipeline information (spider, settings, storage backend).
            Rarely needed for file naming.

        - item (keyword-only, optional):
            The original Item that triggered this download.
            Declared as keyword-only using '*' to maintain backward compatibility
            with older Scrapy versions.

        Why the '*' exists:
        Everything after '*' must be passed by keyword.
        Scrapy uses this to safely extend the API without breaking older pipelines.

        Why we override this method:
        - To implement hash-based storage
        - To separate sellers / albums / image types
        - To avoid filename collisions
        - To support scalable, database-friendly storage

        This method should ONLY handle storage logic.
        It should NOT perform network requests or data parsing.
        """

    # * come back to this and finish the docstring later

    # define the file_path method to determine the file path for each downloaded image using hash-based naming
    def file_path(self, request, response=None, info=None, *, item=None):
        # extract the item context from the request meta, this is the metadata we attached to the request in get_media_requests()
        item = request.meta.get("item", {})
        # get the data from the item meta
        seller = self.normalize_category(item.get("seller", "unknown_seller"))
        category = self.normalize_category(item.get("category", "unknown_category"))
        album_url = item.get("album_url", "unknown_album")

        # define the storage subdirectory based on image type

        # Generate a stable, filesystem-safe identifier for the album
        # - album_url is a string (URLs can be long and unsafe for directory names)
        # - .encode() converts the string to bytes (hash functions operate on bytes)
        # - hashlib.sha1(...) generates a deterministic hash of the album URL
        # - .hexdigest() converts the hash to a readable hexadecimal string
        # - [:10] shortens the hash to keep directory names compact while remaining unique enough
        # Result: the same album URL will always map to the same album directory
        album_hash = hashlib.sha1(album_url.encode()).hexdigest()[:10]

        # Generate a unique, deterministic filename for the image
        # - request.url is the full image URL
        # - hashing the URL guarantees that the same image URL always produces the same filename
        # - using the full hash minimizes the risk of collisions between different image URLs
        # - this avoids relying on remote filenames, which are often duplicated or meaningless
        # Result: image files are uniquely identified by their URL, preventing duplicates and overwrites
        image_hash = hashlib.sha1(request.url.encode()).hexdigest()

        # *----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Build and return the relative file path where the downloaded image will be stored
        # This path is relative to the IMAGES_STORE directory configured in Scrapy settings
        #
        # Directory structure breakdown:
        #
        # 1. seller/
        #    - Top-level directory grouping all images by seller/source
        #
        # 2. category_name_category_text/
        #    - Groups images by category for easier navigation and separation
        #    - Combines both a machine-friendly name and human-readable text
        #
        # 3. category_url_page_number_page_url_album_hash/
        #    - Encodes crawl context (where the album was found)
        #    - Includes:
        #        * category_url  → identifies the category page
        #        * page_number   → pagination index within the category
        #        * page_url      → exact page URL
        #        * album_hash    → short, stable identifier for the album
        #    - Ensures albums from different pages or categories never collide
        #
        # 4. request.meta.get('image_type', 'unknown')/
        #    - Separates images by their semantic role
        #    - Values are injected earlier in get_media_requests()
        #    - Falls back to 'unknown' if image_type was not provided
        #
        # 5. image_hash.jpg
        #    - Filename is the hash of the image URL
        #    - Guarantees a unique, deterministic filename
        #    - Prevents filename collisions and duplicate downloads
        #
        # The final result is a deterministic, collision-resistant storage path
        # that mirrors the crawl structure and supports resumable, large-scale scraping

        return f"{seller}/{category}/{album_hash}/{request.meta.get('image_type', 'unknown')}/{image_hash}.jpg"

    # *-------------------------------------------------------------------------------------------------------------------------------------------------

    # define the function that will save results after image download is complete
    def item_completed(self, results, item, info):
        # initialize the lists to hold the file paths of downloaded images
        # We use setdefault to ensure lists exist, but we might want to clear them if we are re-populating
        # However, for a single item pipeline pass, initialization is fine.
        item["product_images_paths"] = []
        item["size_chart_images_paths"] = []

        for success, file_info in results:
            if success:
                path = file_info["path"]
                # Check for the directory name in the path to identify image type properly
                if "product_image" in path:
                    # if the path contains 'product_image', we append the path to the product_images_paths list in the item
                    item.setdefault("product_images_paths", []).append(path)
                elif "size_chart_image" in path:
                    # if the path contains 'size_chart_image', we append the path to the size_chart_images_paths list in the item
                    item.setdefault("size_chart_images_paths", []).append(path)
        return item
