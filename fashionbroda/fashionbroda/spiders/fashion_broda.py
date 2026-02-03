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


# define a new spider class called FashionBrodaSpider and then it inherits scraping capabilities from scrapy.Spider
class FashionBrodaSpider(scrapy.Spider):
    # name of the spider in this case it is fashion_broda
    name = "fashion_broda"

    # the allowed domains for the spider to scrape
    allowed_domains = ["fashionbroda.x.yupoo.com"]

    # the starting URL for the spider to begin scraping
    start_urls = ["https://fashionbroda.x.yupoo.com/categories/"]

    # parse method to handle the response from the start_url
    # self refers to the instance of the spider class & response is the scrapy response object
    def parse(self, response):
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
        contact = contact.split(":")[-1].strip()

        # *-------------------------------------------------------------------------------------------------------------------------------------------------

        # get the category link
        category_link = response.css(".yupoo-collapse-header a::attr(href)").getall()
        # add a conditional to handle cases where category_link might be None, to prevent errors
        # the for loop iterates through each link in the category_link list, stripping whitespace
        category_link = [link.strip() if link else None for link in category_link]

        # get the category text as it appears on the page
        category_text = response.css(".yupoo-collapse-header a::text").getall()
        # add conditionals to handle cases where category_link or category_text might be None, to prevent errors
        # the for loop iterates through each text in the category_text list, stripping whitespace
        category_text = [text.strip() if text else None for text in category_text]

        # *-------------------------------------------------------------------------------------------------------------------------------------------------

        # use the zip function to combine the three lists into a tuple containing corresponding elements from each list
        # then iterate through each tuple using a for loop and unpack the values into category, category_link, and category_text variables
        for category, link, text in zip(categories, category_link, category_text):
            # yield a dictionary with the extracted data, for every category found on the page
            # so this yield function runs multiple times, and it must be inside the for loop
            yield {
                "seller": seller,
                "contact": contact,
                "category": category,
                "category_text": text,
                # use response.urljoin to convert the relative category link to an absolute URL
                "category_link": response.urljoin(link),
            }
