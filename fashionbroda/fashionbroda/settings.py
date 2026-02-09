# Scrapy settings for fashionbroda project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# import Pathlib to handle file paths
from pathlib import Path

# set the base directory of the project
# Path to the directory containing settings.py
SETTINGS_PATH = Path(__file__).resolve().parent

# Path to the project root (where scrapy.cfg is)
BASE_DIR = SETTINGS_PATH.parent

# *-----------------------------------------------------------------------------------------------

BOT_NAME = "fashionbroda"

SPIDER_MODULES = ["fashionbroda.spiders"]
NEWSPIDER_MODULE = "fashionbroda.spiders"

ADDONS = {}


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "reps_cheap (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Concurrency and throttling settings

# Increase the number of concurrent requests performed by Scrapy (default: 16), to speed up scraping
# These are the number of concurrent requests that will be performed to any single domain
# This sets the global concurrency limit for the scraper
CONCURRENT_REQUESTS = 10

# This sets the concurrency limit per domain
CONCURRENT_REQUESTS_PER_DOMAIN = 10

# This sets a download delay for requests to the same domain
# Setting a download delay can help avoid overwhelming the server and reduce the risk of being blocked
# Here, we can set it to 0 to maximize scraping speed
DOWNLOAD_DELAY = 0.25  # 500 milliseconds of delay between requests to the same domain
# Randomize the download delay to avoid detection, we set it to True to have varied delays
# If we set it to False, the download delay will be fixed as per DOWNLOAD_DELAY setting
RANDOMIZE_DOWNLOAD_DELAY = True

# Disable cookies (enabled by default)
# This increases scraping speed and reduces the chance of being tracked via cookies
COOKIES_ENABLED = False

# Use the Asyncio reactor for better performance with asynchronous code
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
SPIDER_MIDDLEWARES = {
    # Usually empty unless you have custom logic for handling items
    # "reps_cheap.middlewares.RepsCheapSpiderMiddleware": 543,
}

# Enable or disable downloader middlewares
# Downloader middlewares are used to process requests and responses in Scrapy
# They can modify requests before they are sent to the web server
# and process responses before they reach the spider
DOWNLOADER_MIDDLEWARES = {
    # 1. Disable default Scrapy UserAgent (Important!)
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    # 2. Activate YOUR custom rotation middleware
    # Priority 400: Runs early to assign User-Agent and Proxy
    "fashionbroda.middlewares.SessionMiddleware": 400,
    # 3. Request Logging (Helpful to verify it's working)
    # Priority 700: Runs after everything else to see the final headers
    "fashionbroda.middlewares.RequestIdentityLoggingMiddleware": 700,
}

# Define the path to the rotating proxies list
ROTATING_PROXY_LIST_PATH = str(SETTINGS_PATH / "resources/proxies.txt")

# define the user agents file path
USER_AGENTS_LIST_PATH = str(SETTINGS_PATH / "resources/user_agents.txt")

# If a proxy fails, retry the request this many times before giving up, in this case we set it to 3
ROTATING_PROXY_PAGE_RETRY_TIMES = 3

# Do not close the spider when all proxies are unusable
ROTATING_PROXY_CLOSE_SPIDER = False

# Define the ban policy to use when detecting banned requests, in this case we use the default BanPolicy
# ROTATING_PROXY_BAN_POLICY = 'rotating_proxies.policy.DefaultBanPolicy'

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    "fashionbroda.extensions.CleanJobDirExtension": 500,
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "fashionbroda.pipelines.ImagesPipeline": 1,
}

# where to save downloaded images
IMAGES_STORE = str(
    BASE_DIR / "fashionbroda" / "fashionbroda" / "scraped_data" / "images"
)


# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = False
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"

# resume the crawl where it left off in case of interruption
# JOBDIR = "crawls/fashionbroda_job"

# * scrapy crawl "<spider_name>" -s JOBDIR=   --- this overides the JOBDIR setting in settings.py, allowing you to specify a different job directory for each crawl if needed

# *---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

"""
# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "fashionbroda (+http://www.yourdomain.com)"

# Do not obey robots.txt rules
ROBOTSTXT_OBEY = False

# Concurrency and throttling settings
# CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 10
DOWNLOAD_DELAY = 0.5  # 500 milliseconds of delay between requests to the same domain

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "fashionbroda.middlewares.FashionbrodaSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    "fashionbroda.middlewares.FashionbrodaDownloaderMiddleware": 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    "fashionbroda.pipelines.FashionbrodaPipeline": 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"
"""
