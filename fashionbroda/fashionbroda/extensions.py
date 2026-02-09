import os
import shutil

from scrapy import signals


class CleanJobDirExtension:
    """
    This extension automatically deletes the JOBDIR directory when a spider
    finishes successfully. This ensures that the next run starts fresh
    unless the previous run was interrupted mid-operation.
    """

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls()
        # Connect the spider_closed signal to our custom handler
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        return ext

    def spider_closed(self, spider, reason):
        # We only delete the JOBDIR if the spider finished naturally ('finished')
        # If it was interrupted (Ctrl+C), reason will be 'shutdown' or similar,
        # and we leave the directory so it can be resumed later.
        if reason == "finished":
            # Get the JOBDIR from the spider's settings
            jobdir = spider.settings.get("JOBDIR")

            if jobdir:
                if os.path.exists(jobdir):
                    spider.logger.info(
                        f"Spider finished successfully. Cleaning up JOBDIR: {jobdir}"
                    )
                    try:
                        shutil.rmtree(jobdir)
                    except Exception as e:
                        spider.logger.error(f"Failed to delete JOBDIR {jobdir}: {e}")
                else:
                    spider.logger.debug(
                        f"JOBDIR {jobdir} does not exist, skipping cleanup."
                    )
