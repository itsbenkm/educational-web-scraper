# this spider is used to scrape album categories from the fashionbroda.x.yupoo.com website
# it was created using the command : scrapy genspider albums https://fashionbroda.x.yupoo.com/categories/

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

# import json to handle JSON data
import json

# Import scrapy module to gain web scraping capabilities
import scrapy

# import scrapy exceptions to handle exceptions
from scrapy.exceptions import CloseSpider

# import the AlbumItem class from items.py to structure the scraped data
from fashionbroda.items import AlbumItem

# import the BASE_DIR from settings.py ensuring specific path resolution
from fashionbroda.settings import BASE_DIR

# *----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# create a function to validate the structure of the JSON data,
# this is important to ensure that the data we are working with is in the expected format, and to catch any issues with the data early on in the scraping process
# this is because we will be passing the metadata from the fashion_broda.json file to the parse_category method, and we want to ensure that the data is structured correctly before we do so
# pass an argument called raw_ctx which is the raw context data from the fashion_broda.json file, this is the data that we will be validating and structuring before passing it to the parse_category method
def validate_ctx_fields_values(raw_ctx):
    # define the allowed ctx fields for validation
    """
    Validate and clean context fields from JSON data.

    Args:
        raw_ctx (dict): Raw context data from fashion_broda.json

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
    }

    # create a dictionary to hold the validated context data
    clean = {}

    # loop through each allowed ctx field and validate its presence in the raw_ctx dictionary
    for key in ALLOWED_CTX_FIELDS:
        # get the value for the current key from the raw_ctx dictionary, this will be checked from the fashion_broda.json file
        # we do this by calling the get method on the raw_ctx dictionary, get returns the value for the specified key if it exists, otherwise it returns None,
        #  this is useful for handling cases where the key might be missing from the raw_ctx dictionary, which would indicate an issue with the data in the fashion_broda.json file
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


# *----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# Define a new spider class called AlbumsSpider that inherits from scrapy.Spider
class AlbumsSpider(scrapy.Spider):
    # Name of the spider
    name = "albums"
    # The allowed domains for the spider to scrape
    allowed_domains = ["fashionbroda.x.yupoo.com"]

    # Custom export feeds for the scraped data, this is where we define how we want to export the scraped data,
    # in this case we want to export it as a JSON file with UTF-8 encoding, and we want to overwrite the file if it already exists, and we want to specify the fields that we want to include in the exported data
    custom_settings = {
        "JOBDIR": "crawls/albums",
        "LOG_FILE": str(BASE_DIR / "fashionbroda" / "spider_logs" / "albums.log"),
        "LOG_LEVEL": "INFO",
        "FEEDS": {
            str(
                BASE_DIR
                / "fashionbroda"
                / "fashionbroda"
                / "scraped_data"
                / "albums.json"
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
                ],
            }
        },
    }

    # *----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # create a function to read the start_urls from a json file
    # this function is an async generator that yields scrapy.Request objects
    async def start(self):
        """
        Entry point of the spider.
        Reads category URLs from fashion_broda.json
        and schedules category pages for scraping.
        """

        # The starting URL for the spider to begin scraping, which is the categories page of the website
        # the start urls will be read from the fashion_broda.json file

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
                / "fashion_broda.json"
            )

            # open the fashion_broda.json file and read its contents, using a with statement to ensure the file is properly closed after reading
            # the file is opened in read mode, `r` with UTF-8 encoding to handle any special characters
            with open(json_file_path, "r", encoding="utf-8") as json_file:
                # load the JSON data from the file
                # this returns a list of dictionaries, where each dictionary represents a category with its associated metadata, this is the data that we will be using to schedule the category pages for scraping
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
            # validate that all required values of the fields are present and non empty
            try:
                ctx = validate_ctx_fields_values(dict)
            except ValueError as e:
                # log a warning message if the JSON is empty or invalid, this is useful for debugging and monitoring the scraping process, to identify any issues with the data
                self.logger.warning(f"Invalid entry : {e} in entry: {dict}")
                # skip this entry and continue to the next one
                continue
            # check if the dictionary in the fashion_broda.json file is active, if not skip it
            if not dict.get("active", True):
                # if it is not active, continue without failing, onto the next category_url
                continue

            # yield a scrapy.Request for each category URL
            yield scrapy.Request(
                # Give scrapy the URL to crawl, in this case the category URL, from the fashion_broda.json file
                url=ctx["category_link"],
                # Pass the category data as metadata to the parse method, using meta parameter
                # NOTE : only unpack data when you are dealing with data from unknown source
                # and unpack the category dictionary directly, to validate its contents, only if it came from an external source, but for now since I control the fashion_broda.json file, it's safe, to pass the entire category dictionary
                # define my namespace as 'ctx'  and pass the validated context metadata, to avoid confusion with other meta data, such as scrapy default ones, these include 'download_latency', 'depth', 'redirect_urls', 'redirect_times', 'retry_times', 'max_retry_times', etc.
                meta={"ctx": ctx},
                # When the response is received, call the parse_category method to handle it
                callback=self.parse_category,
            )

    # *----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # create a parse method to handle the response from the category URLs and parse the album data from each category page, and then yield the album data as a dictionary
    def parse_category(self, response):
        # pass the metadata from the fashion_broda.json file to the parse_category method
        ctx = response.meta.get("ctx", {})
        # check whether ctx is empty
        if not ctx:
            # log a warning message if ctx is empty
            self.logger.warning(
                f"Context data is missing in the response meta for URL: {response.url}"
            )
            # return early to avoid processing with empty context
            return

        # *----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # page_number is not available on the page, but we can extract it from the URL, if the URL has a page number in it, we can use a regular expression to extract it, otherwise we can set it to 1 for the first page
        # this is useful for pagination and tracking which page the album URL was found on
        active_page = response.css(".pagination__active::text").get()

        # implement a try except block to handle potential errors while converting active_page to an integer
        try:
            # convert active_page to an integer after stripping whitespace
            active_page = int(active_page.strip())
        # if there is a ValueError, (meaning the string could not be converted to an integer) or AttributeError(meaning the string was None and had no strip method), set active_page to 1
        except (ValueError, AttributeError):
            # set the default value to 1
            active_page = 1

        # *----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # select all album containers on the category page
        albums_links = response.css(".categories__children a")

        # loop through each album container to extract album data
        for album in albums_links:
            # extract the album URL from the href attribute of the <a> tag
            album_url = album.attrib.get("href")
            # check if album_url exists
            if not album_url:
                # if it does not exist, skip this album and continue to the next one
                # and log a warning message that the album URL is missing, this is useful for debugging and monitoring the scraping process, to identify any issues with missing data
                self.logger.warning(f"Album URL is missing for album: {album.attrib}")
                continue

            # strip whitespace from the album URL
            album_url = album_url.strip()
            # convert relative album URL to absolute URL using response.urljoin, this is important to ensure that we are working with complete URLs, and to handle cases where the album URL is relative rather than absolute
            album_url = response.urljoin(album_url)

            # pack the data for the album into a dictionary, this includes the metadata from the fashion_broda.json file as well as the album URL and page number
            # create an AlbumItem instance to structure the scraped data, we can pass ctx dictionary using the double asterisks (**) to unpack its contents into the AlbumItem fields,
            # this can be done cause we safely validated that the ctx dictionary contains only the fields defined in the AlbumItem class
            item = AlbumItem(
                {
                    # unpack the validated ctx metadata to be passed to the albumitem for output
                    **ctx,
                    "page_url": response.url,
                    "page_number": active_page,
                    "album_url": album_url,
                }
            )
            # yield the album item
            yield item

        # *----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # get the next page link from the page
        next_page = response.css("a[title='next page']::attr(href)").get()

        # return a full URL for the next page using response.urljoin to handle relative URLs
        next_page = response.urljoin(next_page) if next_page else None

        # check if there is a next page link
        if next_page:
            # if there is a next page, yield a response.follow  to crawl the next page
            yield response.follow(
                # the spider will crawl the next page URL to extract more album data, this allows us to crawl through all the pages in the category until there are no more next page links
                next_page,
                # pass the metadata to the next page that is crawled
                meta={"ctx": ctx},
                # then call the parse_category method to handle the response from the next page,
                # this creates a recursive crawling effect that allows us to crawl through all the pages in the category until there are no more next page links
                callback=self.parse_category,
            )
