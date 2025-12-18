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

    def get_available_years(self, html_content: str = None) -> list[str]:
        """
        Extracts available years from the competition archive page's dropdown.
        Can process either live URL content or a provided HTML string for testing.

        Args:
            html_content: Optional. If provided, uses this HTML string for parsing
                          instead of navigating to the live URL.

        Returns:
            A list of strings, where each string represents an available year (e.g., "2023-24").
        """
        self.logger.info("Attempting to get available years...")
        try:
            if html_content:
                self.logger.debug("Setting page content from provided HTML.")
                self.page.set_content(html_content)
            else:
                base_url = self.config['data_source']['base_url']
                self.logger.debug(f"Navigating to {base_url} to get live content.")
                self.page.goto(base_url, timeout=self.config['scraping']['timeout_seconds'] * 1000)

            year_selector = self.config['scraping']['selectors']['year_dropdown']
            self.logger.debug(f"Using year dropdown selector: {year_selector}")

            years = []
            # Wait for the selector to be present in the DOM
            self.page.wait_for_selector(year_selector, state='attached', timeout=self.config['scraping']['timeout_seconds'] * 1000)
            
            # Get all option elements within the year dropdown
            option_elements = self.page.locator(f"{year_selector} option").all()

            for option in option_elements:
                value = option.get_attribute("value")
                if value and value != "":  # Exclude the placeholder option
                    years.append(value)
            
            self.logger.info(f"Successfully extracted {len(years)} available years.")
            return years

        except Exception as e:
            self.logger.error(f"Failed to get available years: {e}")
            raise
