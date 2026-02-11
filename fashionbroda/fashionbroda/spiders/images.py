# This spider was created using the command: scrapy genspider images https://fashionbroda.x.yupoo.com/categories

"""
TODO : CONCEPTS TO PUT IN MIND

Defensive programming: Notice how we added checks to ensure that if certain elements are missing from the page, our spider won't crash.
This is crucial for web scraping, as web pages can change or have inconsistent structures.

Defensive programming is a practice where you write code that anticipates and handles potential errors or unexpected situations.
This should be done at system boundaries :

🌐 The web (Scrapy, APIs, HTML, JSON)
👤 Users (forms, input fields)
🔌 External services (payment gateways, auth providers)
📂 Files, env vars, configs
🌍 Network, time, OS

"""

# import json to handle json data
import json

# import regex
import re

# Import scrapy module to gain web scraping capabilities
import scrapy

# import scrapy exceptions to handle exceptions
from scrapy.exceptions import CloseSpider

# import the ImageItem class from items.py to structure the scraped data
from fashionbroda.items import ImageItem

# import the BASE_DIR from settings.py ensuring specific path resolution
from fashionbroda.settings import BASE_DIR

# *-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# create a function to validate the structure of the JSON data,
# this is important to ensure that the data we are working with is in the expected format, and to catch any issues with the data early on in the scraping process
# this is because we will be passing the metadata from the albums.json file to the parse_album method, and we want to ensure that the data is structured correctly before we do so
# pass an argument called raw_ctx which is the raw context data from the albums.json file, this is the data that we will be validating and structuring before passing it to the parse_album method
def validate_ctx_fields_values(raw_ctx):
    # define the allowed ctx fields for validation
    """
    Validate and clean context fields from JSON data.

    Args:
        raw_ctx (dict): Raw context data from albums.json

    Returns:
        dict: Validated and cleaned context data with stripped string values

    Raises:
        ValueError: If any required field is missing or empty
    """
    ALLOWED_CTX_FIELDS = {
        "seller",
        "contact",
        "category",
        "category_text",
        "category_link",
        "page_url",
        "page_number",
        "album_url",
    }

    # create a dictionary to hold the validated context data
    clean = {}

    # loop through each allowed ctx field and validate its presence in the raw_ctx dictionary
    for key in ALLOWED_CTX_FIELDS:
        # get the value for the current key from the raw_ctx dictionary, this will be checked from the albums.json file
        # we do this by calling the get method on the raw_ctx dictionary, get returns the value for the specified key if it exists, otherwise it returns None,
        #  this is useful for handling cases where the key might be missing from the raw_ctx dictionary, which would indicate an issue with the data in the albums.json file
        value = raw_ctx.get(key)

        # check if the ctx field have missing or empty values, and none values,
        # this is important to ensure that we are working with complete and valid data, and to catch any issues with the data early on in the scraping process
        if value is None or (isinstance(value, str) and not value.strip()):
            # raise a ValueError if any of the required fields are missing or empty, this is important to ensure that we are working with complete and valid data,
            # and to catch any issues with the data early on in the scraping process
            raise ValueError(f"Missing or empty field: {key}")
        # add the validated key-value pair to the clean dictionary, stripping any leading or trailing whitespace from string values
        # this is done after checking that the string instace is not empty, to avoid calling strip on a None value, which would raise an AttributeError
        clean[key] = value.strip() if isinstance(value, str) else value
    # return the validated context data
    return clean


# *--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# create a class called ImagesSpider that inherits from scrapy.Spider, this is the base class for all spiders in Scrapy, and it provides the basic functionality for crawling and parsing web pages
class ImagesSpider(scrapy.Spider):
    # name of the spider in this case it is images
    name = "images"
    # the allowed domains for the spider to scrape, this is a security measure to prevent the spider from crawling unintended websites,
    # and to ensure that we are only scraping data from the specified domain, which in this case is fashionbroda.x.yupoo.com
    allowed_domains = ["fashionbroda.x.yupoo.com"]

    # Custom export feeds for the scraped data, this is where we define how we want to export the scraped data,
    # in this case we want to export it as a JSON file with UTF-8 encoding, and we want to overwrite the file if it already exists, and we want to specify the fields that we want to include in the exported data
    custom_settings = {
        "JOBDIR": "crawls/images",
        "LOG_FILE": str(BASE_DIR / "fashionbroda" / "spider_logs" / "images.log"),
        "LOG_LEVEL": "INFO",
        "FEEDS": {
            # ----------------------------------------
            # RAW crawl output (URLs)
            # ----------------------------------------
            str(
                BASE_DIR
                / "fashionbroda"
                / "fashionbroda"
                / "scraped_data"
                / "images.json"
            ): {
                "format": "json",
                "encoding": "utf8",
                # overwrite the file if it already exists,
                # this is important to ensure that we are not appending to an old file with potentially outdated data, and to ensure that we are working with fresh data each time we run the spider
                "overwrite": True,
                # fields to include in the exported data, this is important to ensure that we are exporting the data in a structured format, and to specify which fields we want to include in the exported data
                "fields": [
                    "seller",
                    "contact",
                    "category",
                    "category_text",
                    "category_link",
                    "page_url",
                    "page_number",
                    "album_url",
                    "product_images",
                    "size_chart_images",
                    "product_data",
                ],
            },
            # ----------------------------------------
            # DB-READY output (file paths)
            # ----------------------------------------
            str(
                BASE_DIR
                / "fashionbroda"
                / "fashionbroda"
                / "scraped_data"
                / "images_paths.json"
            ): {
                "format": "json",
                "encoding": "utf8",
                # overwrite the file if it already exists,
                # this is important to ensure that we are not appending to an old file with potentially outdated data, and to ensure that we are working with fresh data each time we run the spider, and to ensure that we are working with the correct file paths for the images, which can be used for further processing and analysis later on in the data processing pipeline
                "overwrite": True,
                # fields to include in the exported data, this is important to ensure that we are exporting the data in a structured format, and to specify which fields we want to include in the exported data, in this case we want to include the same fields as the raw crawl output, but instead of including the image URLs, we want to include the file paths for the downloaded images, which can be used for further processing and analysis later on in the data processing pipeline
                "fields": [
                    "seller",
                    "contact",
                    "category",
                    "category_text",
                    "category_link",
                    "page_url",
                    "page_number",
                    "album_url",
                    "product_images_paths",
                    "size_chart_images_paths",
                    "product_data",
                ],
            },
        },
    }

    # *--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # create a function to read the start_urls from the albums.json file, this is important to ensure that we are starting our scraping process with the correct URLs,
    # and to allow us to easily update the start URLs by simply updating the albums.json file
    # this function is an async function because it will be called by Scrapy when the spider starts,
    # and it allows us to perform asynchronous operations such as reading from a file without blocking the main thread of execution,
    # which is important for maintaining the responsiveness of the spider and allowing it to perform other tasks while waiting for the file reading operation to complete
    async def start(self):
        """
        Entry point of the spider.
        Reads album URLs from albums.json
        and schedules albums for scraping.
        """

        # The starting URL for the spider to begin scraping, which is the categories page of the website
        # the start urls will be read from the albums.json file

        # implement a try catch block to handle potential file reading errors
        try:
            """
            TODO
            # define the base directory, this is the directory where the current script is located, this is useful to ensure that we are reading the correct file, regardless of where the script is run from
            # __file__ = path to THIS Python file (the spider file)
            # .resolve() = convert it to an absolute path (no ../ or symlinks)
            # .parents[1] = go UP one directory from this file, this gets us to the project root directory
            base_dir = Path(__file__).resolve().parents[1]
            """

            # define the path to the fashion_broda.json file, which is located in the data directory in the project root directory
            json_file_path = (
                BASE_DIR
                / "fashionbroda"
                / "fashionbroda"
                / "scraped_data"
                / "albums.json"
            )

            # open the albums.json file and read its contents, using a with statement to ensure the file is properly closed after reading
            # the file is opened in read mode, `r` with UTF-8 encoding to handle any special characters
            with open(json_file_path, "r", encoding="utf-8") as json_file:
                # load the JSON data from the file
                # this returns a list of dictionaries, where each dictionary represents an album with its associated metadata, this is the data that we will be using to schedule the album pages for scraping
                data = json.load(json_file)

        # account for exceptions that may occur during file reading
        # account for the file not being found error
        except FileNotFoundError:
            # log the error message that the JSON file was not found at the specified path, this is useful for debugging and monitoring the scraping process, to identify any issues with missing files
            self.logger.error(f"JSON file not found at: {json_file_path}")
            raise CloseSpider("JSON file not found")
        # account for JSON decoding errors, which occur when the file is not in valid JSON format
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON format: {e}")
            raise CloseSpider("Invalid JSON file")
        # account for any other unexpected exceptions that may occur during file reading
        except Exception as e:
            self.logger.error(f"Unexpected error reading JSON file: {e}")
            raise CloseSpider("Error reading JSON file")

        # *----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # loop through each entry in the data list
        for dict in data:
            # validate that all required fields are present and non empty
            try:
                ctx = validate_ctx_fields_values(dict)
            except ValueError as e:
                # log a warning message if the JSON structure is invalid, this is useful for debugging and monitoring the scraping process, to identify any issues with the data
                self.logger.warning(f"Invalid entry : {e} in entry: {dict}")
                # skip this entry and continue to the next one
                continue
            # yield a scrapy.Request for each album URL
            yield scrapy.Request(
                # Give scrapy the URL to crawl, in this case the album URL, from the albums.json file
                url=ctx["album_url"],
                # Pass the album data as metadata to the parse method, using meta parameter
                # NOTE : only unpack data when you are dealing with data from unknown source
                # and unpack the album dictionary directly, to validate its contents, only if it came from an external source, but for now since I control the fashion_broda.json file, it's safe, to pass the entire album dictionary
                # define my namespace as 'ctx'  and pass the validated context metadata, to avoid confusion with other meta data, such as scrapy default ones, these include 'download_latency', 'depth', 'redirect_urls', 'redirect_times', 'retry_times', 'max_retry_times', etc.
                meta={"ctx": ctx},
                # When the response is received, call the parse_album method to handle it
                callback=self.parse_album,
            )

    # *----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # create a method to parse the albums
    def parse_album(self, response):
        # extract the album metadata from the response meta, this is the metadata that we passed from the parse method when we scheduled the album pages for scraping
        ctx = response.meta.get("ctx", {})
        # validate the extracted context data to ensure it has all required fields and is properly structured before using it in the parsing logic
        try:
            ctx = validate_ctx_fields_values(ctx)
        except ValueError as e:
            # log a warning message if the JSON structure is invalid, this is useful for debugging and monitoring the scraping process, to identify any issues with the data
            self.logger.warning(f"Invalid context data: {e} in context: {ctx}")
            # skip further processing for this response and return early
            return

        # Get individual product image links from the album page
        product_image_url = response.xpath(
            '//img[contains(@class,"image__portrait")]/@data-origin-src'
        ).getall()

        # this will return a list of image URLs, and we use strip to remove any leading or trailing whitespace from the URLs,
        # which can help to ensure that we are working with clean and valid URLs when we create the full URLs for the images
        product_image_url = [url.strip() for url in product_image_url]

        # create a full URL for each image by joining the base URL with the extracted relative URLs
        product_image = [response.urljoin(url) for url in product_image_url]

        # Get the sizing-data-sheet
        size_chart_path = response.xpath(
            '//img[contains(@class,"image__landscape")]/@data-origin-src'
        ).getall()

        # this will return a list of image URLs, and we use strip to remove any leading or trailing whitespace from the URLs,
        # which can help to ensure that we are working with clean and valid URLs when we create the full URLs for the images
        size_chart_path = [url.strip() for url in size_chart_path]

        # create a full URL for each sizing-data-sheet image by joining the base URL with the extracted relative URLs
        size_chart_images = [response.urljoin(path) for path in size_chart_path]

        # Get product description data, from the meta description tag in sources tab in dev tools
        # and safeguard if the pagedoes not have a description meta tag
        raw_description = response.xpath("//meta[@name='description']/@content").get()

        product_description = raw_description.split("\n") if raw_description else []

        # Create a dictionary to hold the product description data
        product_data = {}

        # *-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        #!IMPORTANT : DO NOT DO EXTENSIVE PROCESSING HERE, KEEP IT LIGHTWEIGHT, DATA CLEANSING SHOULD BE DONE IN THE PIPELINES.PY FILE
        """NOTE:
            This spider performs partial normalization of product descriptions.
            Some fields (e.g. price) may appear as strings or integers depending
            on source formatting. All final typing, schema enforcement, and cleanup
            MUST be handled in pipelines or post-processing.
            
            This approach keeps the spider efficient and focused on data extraction.
        """

        # create a loop to split the product description data into key-value pairs
        for data in product_description:
            # check if the data contains a colon
            if ":" in data:
                # split the data into key and value
                key, value = data.split(":", 1)  # split ONLY once

                # strip convert key to lowercase and replace bullet points with whitespace then strip the whitespace
                # Remove all bullet-like Unicode characters
                clean_key = (
                    re.sub(r"[•●・◦◘○◉⦿⦾▪▫]", "", key).lower().strip().replace(" ", "_")
                )

                # strip whitespace from value
                clean_value = value.strip()

                # Try to convert price to int
                # check whether the clean_key is 'price', using the equality operator (==)
                if clean_key == "price":
                    # Filter out non-numeric characters (like '$', '¥', spaces) so only digits remain
                    # This is done using a generator expression inside the join() method, which iterates over each character in the clean_value string and includes only those that are digits, effectively removing any currency symbols or formatting characters.
                    # then joins them into one clean numeric string that can be converted to an integer, this is important to ensure that we are working with clean and consistent price data, which can be useful for analysis and comparison later on in the data processing pipeline
                    numeric_string = "".join(
                        character for character in clean_value if character.isdigit()
                    )

                    # try to convert the cleaned price string to an integer
                    try:
                        # convert the clean numerical string to an integer
                        clean_value = int(numeric_string)
                    # raise a value error if conversion fails
                    except ValueError:
                        # instead of failing, just pass the value as is to the json output
                        pass

                # add the key-value pair to the product_data dictionary
                # strip whitespace, convert key to lowercase and replace spaces with underscores
                product_data[clean_key] = clean_value

        # *-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # pack the data for the image into a dictionary, this includes the metadata from the images.json file as well as the image URL and page number
        # create an ImageItem instance to structure the scraped data, we can pass ctx dictionary using the double asterisks (**) to unpack its contents into the ImageItem fields,
        # this can be done cause we safely validated that the ctx dictionary contains only the fields defined in the ImageItem class
        item = ImageItem(
            {
                # unpack the validated ctx metadata to be passed to the imageitem for output
                **ctx,
                # add the product images to the item, this is the list of full URLs for the product images that we extracted from the album page
                "product_images": product_image,
                # add the size chart images to the item, this is the list of full URLs for the size chart images that we extracted from the album page
                "size_chart_images": size_chart_images,
                # add the product data to the item, this is the dictionary of product description data that we extracted from the album page, this includes key-value pairs for the product description, such as price, material, etc.
                "product_data": product_data,
            }
        )
        # yield the image item
        yield item
