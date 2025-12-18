import logging
from playwright.sync_api import sync_playwright, Page, BrowserContext, Browser
from tanulmanyi_versenyek.common.config import get_config

class WebsiteDownloader:
    """
    Manages Playwright browser lifecycle and provides methods for web scraping.
    """
    def __init__(self, config: dict, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None

    def __enter__(self):
        """
        Initializes Playwright, launches a browser, and creates a new page.
        """
        self.logger.info("Initializing Playwright and launching browser...")
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.config['scraping']['headless'])
            self.context = self.browser.new_context(user_agent=self.config['scraping']['user_agent'])
            self.page = self.context.new_page()
            self.logger.info("Browser launched and page created.")
            return self
        except Exception as e:
            self.logger.error(f"Failed to initialize Playwright or launch browser: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Closes the browser and stops Playwright.
        """
        self.logger.info("Closing browser and stopping Playwright...")
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.logger.info("Playwright stopped.")
