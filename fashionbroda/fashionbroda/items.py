# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

# This file defines the data structure for the items we will be scraping.
# We create a class that inherits from scrapy.Item, and then we define the fields we want to scrape as scrapy.Field().
# this is schema validation for our scraped data, it helps to ensure that the data we scrape is structured and consistent,
# and it also makes it easier to export the data in a structured format like JSON or CSV.

# * We should separate the item definitions into different classes based on the type of data we are scraping,
# * for example, we can have a FashionbrodaItem class for the main category data,
# * and an AlbumItem class for the album data, this helps to keep our code organized and makes it easier to manage different types of data.
# * it also makes it easier to extend our code in the future if we want to add more fields or types of data.


# we create the base item class to be inherited by other item classes
# this is useful for code reusability and to avoid duplication of common fields across different item classes, such as seller, contact, category, category_text, and category_link
# which are common fields for both the main category data and the album data
# the fashionbrodaitem class is the base item class, this is useful for code reusability and to avoid duplication of common fields across different item classes, such as seller, contact, category, category_text, and category_link
class FashionbrodaItem(scrapy.Item):
    seller = scrapy.Field()
    contact = scrapy.Field()
    category = scrapy.Field()
    category_text = scrapy.Field()
    category_link = scrapy.Field()


# The AlbumItem class defines the fields for the album data we want to scrape from the album pages, such as page_url, page_number, and album_url.
# it also inherits from the BaseFashionbrodaItem class to include the common fields for both the main category data and the album data, such as seller, contact, category, category_text, and category_link.
class AlbumItem(FashionbrodaItem):
    # define the fields for the album item,
    # this is the data structure for the album data that we will be scraping from the album pages, this includes the metadata about the album as well as
    # the fields for the album data itself, such as the image URLs and descriptions
    page_url = scrapy.Field()
    page_number = scrapy.Field()
    album_url = scrapy.Field()


# we create the ImagesItem class that defines the field for the image data we want to scrape from the albums
# it will inherit from the AlbumItem class
class ImageItem(AlbumItem):
    # define the fields for product images in fashionbroda webpage
    # define the fields for the images
    product_images = scrapy.Field()
    size_chart_images = scrapy.Field()
    product_data = scrapy.Field()
