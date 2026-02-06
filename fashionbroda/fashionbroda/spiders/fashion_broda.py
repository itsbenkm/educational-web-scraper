# this spider was created using the command:
# scrapy genspider fashion_broda https://fashionbroda.x.yupoo.com/categories/

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

# import scrapy module to gain web scraping capabilities
import scrapy

# import the FashionbrodaItem class from items.py to structure the scraped data
from fashionbroda.items import FashionbrodaItem

# import the BASE_DIR from settings.py ensuring specific path resolution
from fashionbroda.settings import BASE_DIR


# define a new spider class called FashionBrodaSpider and then it inherits scraping capabilities from scrapy.Spider
class FashionBrodaSpider(scrapy.Spider):
    # name of the spider in this case it is fashion_broda
    name = "fashion_broda"

    # the allowed domains for the spider to scrape
    allowed_domains = ["fashionbroda.x.yupoo.com"]

    # the starting URL for the spider to begin scraping
    start_urls = ["https://fashionbroda.x.yupoo.com/categories/"]

    # custom export feeds
    custom_settings = {
        "FEEDS": {
            BASE_DIR
            / "fashionbroda"
            / "fashionbroda"
            / "scraped_data"
            / "fashion_broda.json": {
                "format": "json",
                "encoding": "utf8",
                "overwrite": True,
                "fields": [
                    "seller",
                    "contact",
                    "category",
                    "category_text",
                    "category_link",
                ],
            },
        }
    }

    # list of clean categories to scrape
    categories = [
        "All categories",
        "Contact Info",
        "Brands",
        "Chrome Hearts",
        "Acne Studios",
        "Louis Vuitton",
        "Balenciaga",
        "Moncler",
        "Miu Miu",
        "Gucci",
        "Maison Margiela",
        "Dior",
        "Loro Piana",
        "Ralph Lauren",
        "The North Face",
        "Thom Browne",
        "Prada",
        "AMI",
        "Burberry",
        "Brunello Cucinelli",
        "Celine",
        "Bottega Veneta",
        "Canada Goose",
        "Fendi",
        "Loewe",
        "Chanel",
        "Stone Island",
        "Saint Laurent",
        "Moose Knuckles",
        "Max Mara",
        "Mackage",
        "Other Brands",
        "Uncategorized Album",
    ]

    # *-------------------------------------------------------------------------------------------------------------------------------------------------

    # parse method to handle the response from the start_url
    # self refers to the instance of the spider class & response is the scrapy response object
    def parse(self, response):
        # assign the categories list to a local variable for easier access
        categories = self.categories

        # *-------------------------------------------------------------------------------------------------------------------------------------------------

        # extract the seller name from the page, and strip whitespace
        seller = response.css("h1::text").get()
        # add a conditional to handle cases where seller might be None, to prevent errors
        seller = seller.strip() if seller else None

        # *-------------------------------------------------------------------------------------------------------------------------------------------------

        # get the contact of the seller and strip whitespace
        contact = response.css("pre::text").get()
        # add a conditional to handle cases where contact might be None, to prevent errors
        contact = contact.strip() if contact else None
        # split the contact at the point where there is a colon and then strip whitespace from each part
        # keep only the part after the colon (the actual contact info)
        if contact and ":" in contact:
            # split the contact string at the first occurrence of ":" and take the second part, then strip whitespace from it
            contact = contact.split(":", 1)[-1].strip()
        else:
            self.logger.warning(
                f"Contact information is missing or does not contain a colon: '{contact}'"
            )

        # *-------------------------------------------------------------------------------------------------------------------------------------------------

        # select all the <a> elements that hold the category links and text from the DOM for all categories
        # that is why we are not using .get() or .getall() here, because we want the entire list of elements
        category_node = response.css(".yupoo-collapse-header a")

        # check whether the category node length matches the expected number of categories, provided above in the categories list
        # this is a defensive programming technique to catch any discrepancies in the page structure, we use the `!=` operator to check for inequality
        if len(category_node) != len(categories):
            self.logger.warning(
                f"Expected {len(categories)} categories, but found {len(category_node)} categories on the page."
            )

        # loop through each category node and extract the href attribute (the link) and the text content as it appears on the page
        # we use enumerate to get both the index and the node itself,
        for index, node in enumerate(category_node):
            # get the link from the href attribute
            category_link = node.attrib.get("href")
            # check if category_link exists before stripping whitespace
            category_link = category_link.strip() if category_link else None
            # then convert relative link to absolute URL
            category_link = response.urljoin(category_link) if category_link else None

            # get the text and check if it exists
            text = node.css("::text").get()
            # then strip whitespace, and handle cases where text might be None
            text = text.strip() if text else None

            # Defensive programming: Log a warning if link or text is missing for a category
            if not category_link or not text:
                self.logger.warning(
                    f"Missing data for category at index {index}: link='{category_link}', text='{text}'"
                )

            # Attach the clean category by position (order-based mapping).
            # We first check that the current index exists in the clean categories list
            # to avoid IndexError if the page structure changes (e.g., extra or missing categories).
            # If no corresponding clean category exists, we fall back to None to keep the spider safe
            # and make the mismatch visible for later inspection.
            category = categories[index] if index < len(categories) else None

            # *-------------------------------------------------------------------------------------------------------------------------------------------------

            # yield a dictionary item with the extracted data,using constructor-style for every category found on the page
            # so this yield function runs multiple times, and it must be inside the for loop
            yield FashionbrodaItem(
                {
                    "seller": seller,
                    "contact": contact,
                    "category": category,
                    "category_text": text,
                    "category_link": category_link,
                }
            )
