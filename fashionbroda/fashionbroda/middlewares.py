# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html


# useful for handling different item types with a single interface


# import random module to select random user agents
import random

# threading is used to ensure concurrent access to shared resources is handled safely
# threading ensures that when multiple threads access shared data, they do so in a controlled manner to prevent data corruption or inconsistencies
# threading is particularly important in web scraping scenarios where multiple requests may be processed simultaneously
import threading

# import cycle from itertools to cycle through proxies
from itertools import cycle


# custom middleware to rotate user agents
class SessionMiddleware:
    # use the @classmethod decorator to define a class method, which is a method that is bound to the class and not the instance of the class,
    # it can access class variables and methods, before any instance of the class is created
    @classmethod
    # this function needs to read the user agents from a file
    # crawler is passed as an argument to access settings, the from_crawler method is a standard way in Scrapy to create middleware instances with access to crawler settings
    def from_crawler(cls, crawler):
        # Load user agents from a file specified in settings
        path = crawler.settings.get("USER_AGENTS_LIST_PATH")
        # Read the user agents from the file
        with open(path, "r") as agents:
            # strip any whitespace, "line.strip()"
            # and ignore empty lines, "if line.strip()"
            user_agent = [line.strip() for line in agents if line.strip()]

        # load proxies from a file specified in settings
        path = crawler.settings.get("ROTATING_PROXY_LIST_PATH")
        # read the proxies from the file
        with open(path, "r") as proxy_file:
            # strip any whitespace, "line.strip()"
            # and ignore empty lines, "if line.strip()"
            proxies = [line.strip() for line in proxy_file if line.strip()]
            # return an instance of the middleware with the loaded proxies, user agents, and crawler passed as arguments to the constructor
        return cls(user_agent, proxies, crawler)

    # define the init method to accept a list of user agents,proxies, and crawler through the constructor, then passing them as arguments
    def __init__(self, user_agent, proxies, crawler):
        self.agent_list = user_agent  # store the list of user agents
        self.proxies_cycle = cycle(proxies)  # Use cycle to rotate through proxies
        self.crawler = crawler  # store the crawler instance
        # here we define the current agent and current proxy to be used
        # we use the next keyword to get the next item from the cycle,
        # in this case we are using it go get the first proxyfrom a predefined list
        self.current_proxy = next(self.proxies_cycle)

        # randomly select a user agent from the list to start with
        self.current_agent = random.choice(self.agent_list)

        # set the user agent and proxy count for the iteration logic to zero
        # these will be used to count how many requests have been made with the current user agent and proxy
        self.user_agent_count = 0
        self.proxy_count = 0

        # set the max number of requests per user agent and proxy before rotating
        self.max_requests_per_agent = 500  # max requests per user agent
        self.max_requests_per_proxy = 4000  # max requests per proxy

        # Lock for thread-safe operations
        # where there are shared resources being accessed by multiple threads, we use a lock to ensure that only one thread can access the shared resource at a time
        # in this case, we use a lock to protect access to the user agent and proxy rotation logic, where multiple threads might try to rotate user agents or proxies simultaneously
        # leading to race conditions or inconsistent states, race conditions occur when multiple threads access shared data concurrently, and the final outcome depends on the timing of their execution
        self.lock = threading.Lock()

    # process_request is a method that is called for each request that goes through the downloader middleware
    # here we define how to process each request, specifically, the logic for rotating user agents and proxies
    def process_request(self, request):
        # Use a lock to ensure thread-safe access to shared resources
        with self.lock:
            # Rotate user agent if the count exceeds the max requests per agent
            # if the user_agent_count is greater than or equal to the max_requests_per_agent, which is 500
            if self.user_agent_count >= self.max_requests_per_agent:
                # then we get the next user agent from the cycle, through random choice
                self.current_agent = random.choice(self.agent_list)
                self.user_agent_count = 0  # Reset the count after rotation
                # log the rotated user agent
                self.crawler.spider.logger.info(
                    f"Rotated User-Agent to: {self.current_agent}"
                )

            # Rotate proxy if the count exceeds the max requests per proxy, in this case 4000
            # if the proxy_count is greater than or equal to the max_requests_per_proxy, which is 4000
            if self.proxy_count >= self.max_requests_per_proxy:
                # then we get the next proxy from the cycle
                self.current_proxy = next(self.proxies_cycle)
                self.proxy_count = 0  # Reset the count after rotation
                # log the rotated proxy
                self.crawler.spider.logger.info(
                    f"Rotated Proxy to: {self.current_proxy}"
                )

            # Set the User-Agent header and proxy for the outgoint https scrapy request
            request.headers["User-Agent"] = self.current_agent
            request.meta["proxy"] = self.current_proxy

            # Increment the counts for user agent and proxy usage, per request
            self.user_agent_count += 1
            self.proxy_count += 1

    # ----------------------------------------------------------------------------------------------
    # AI

    # ban detection method to handle banned requests
    def process_response(self, request, response):
        # Check for HTTP status codes that indicate a ban
        if response.status in [
            403,
            429,
            503,
        ]:  # 403 Forbidden, 429 Too Many Requests, 503 Service Unavailable
            # we use a lock to ensure thread-safe access to shared resources
            with self.lock:
                # Log the ban event
                self.crawler.spider.logger.warning(
                    f"Request banned with status {response.status}. Rotating proxy and user-agent."
                )

                # Rotate to the next proxy, in the cycle of proxies
                self.current_proxy = next(self.proxies_cycle)
                self.proxy_count = 0  # Reset the count after rotation
                self.crawler.spider.logger.info(
                    f"Rotated Proxy to: {self.current_proxy}"
                )

                # Rotate to a new user agent, that is randomized
                self.current_agent = random.choice(self.agent_list)
                self.user_agent_count = 0  # Reset the count after rotation
                self.crawler.spider.logger.info(
                    f"Rotated User-Agent to: {self.current_agent}"
                )

            # Update the request with the new proxy and user agent
            request.meta["proxy"] = self.current_proxy
            request.headers["User-Agent"] = self.current_agent

            # Allow the request to be retried by setting dont_filter to True
            request.dont_filter = True

            # Return the modified request to retry it
            return request

        # If the response status is not indicative of a ban, return the response as is
        return response

    # Handle exceptions such as connection errors or timeouts
    def process_exception(self, request, exception):
        with self.lock:
            # Log the exception event
            self.crawler.spider.logger.warning(
                f"Exception encountered: {exception}. Rotating proxy and user-agent."
            )

            # Rotate to the next proxy
            self.current_proxy = next(self.proxies_cycle)
            self.proxy_count = 0
            self.crawler.spider.logger.info(f"Rotated Proxy to: {self.current_proxy}")

            # Rotate to a new user agent
            self.current_agent = random.choice(self.agent_list)
            self.user_agent_count = 0
            self.crawler.spider.logger.info(
                f"Rotated User-Agent to: {self.current_agent}"
            )

        # Update the request with the new proxy and user agent
        request.meta["proxy"] = self.current_proxy
        request.headers["User-Agent"] = self.current_agent

        # Allow the request to be retried
        request.dont_filter = True

        # Return the modified request to retry it
        return request


# Custom middleware to log request identity details
class RequestIdentityLoggingMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def __init__(self, crawler):
        self.crawler = crawler

    def process_request(self, request):
        # define user_agent, this will look at the request headers to get the User-Agent
        # request.headers is a dictionary-like object, so we use .get() to retrieve the User-Agent
        # If User-Agent is not found, default to an empty byte string
        # Decode bytes to string for logging, and ignore errors during decoding, errors="ignore",errors might occur if there are non-UTF-8 bytes
        user_agent = request.headers.get("User-Agent", b"").decode(errors="ignore")

        # define proxy, this will look at the request meta to get the proxy being used
        # if there is no proxy set, default to "no proxy"
        proxy = request.meta.get("proxy", "no proxy")
        # Log the details using the spider's logger
        self.crawler.spider.logger.info(
            f"[REQUEST] proxy={proxy} | user_agent={user_agent} | url={request.url}"
        )


# ----------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------


"""
class FashionbrodaSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    async def process_start(self, start):
        # Called with an async iterator over the spider start() method or the
        # matching method of an earlier spider middleware.
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class FashionbrodaDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
"""
