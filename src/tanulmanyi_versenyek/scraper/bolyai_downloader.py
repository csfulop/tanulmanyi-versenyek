import logging
import time
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

    def wait_for_dropdown_populated(self, selector: str, timeout: int = 5000):
        """Wait for a dropdown to be populated with non-empty options."""
        self.page.wait_for_function(
            f"document.querySelectorAll('{selector} option[value]:not([value=\"\"])').length > 0",
            timeout=timeout
        )

    def get_available_options(self, selector: str) -> list[str]:
        """Get available option values from a dropdown."""
        options = []
        option_elements = self.page.locator(f"{selector} option").all()
        for option in option_elements:
            value = option.get_attribute("value")
            if value and value != "":
                options.append(value)
        return options

    def get_html_for_combination(self, year: str, grade_value: str, round_name: str) -> str | None:
        """
        Navigates a web page, selects options from dropdowns, and returns the page's HTML.

        Args:
            year: The year to select in the dropdown.
            grade_value: The full grade value to select (e.g., "8. osztály - általános iskolai kategória").
            round_name: The name of the round to select.

        Returns:
            The HTML content of the page after selections, or None if it fails after retries.
        """
        base_url = self.config['data_source']['base_url']
        max_retries = self.config['scraping']['max_retries']
        timeout = self.config['scraping']['timeout_seconds'] * 1000
        delay = self.config['scraping']['delay_seconds']

        selectors = self.config['scraping']['selectors']
        year_selector = selectors['year_dropdown']
        grade_selector = selectors['grade_dropdown']
        round_selector = selectors['round_dropdown']

        for attempt in range(max_retries):
            self.logger.info(f"Attempt {attempt + 1}/{max_retries} for {year}, grade '{grade_value}', round '{round_name}'")
            try:
                if self.page:
                    self.page.close()
                self.page = self.context.new_page()
                
                self.page.goto(base_url, timeout=timeout, wait_until='networkidle')

                self.page.select_option(year_selector, year)
                self.wait_for_dropdown_populated(grade_selector, timeout)

                available_grades = self.get_available_options(grade_selector)
                if grade_value not in available_grades:
                    self.logger.warning(f"Grade '{grade_value}' not available for year {year}. Available: {available_grades}")
                    return None

                self.page.select_option(grade_selector, grade_value)
                self.wait_for_dropdown_populated(round_selector, timeout)

                available_rounds = self.get_available_options(round_selector)
                if round_name not in available_rounds:
                    self.logger.warning(f"Round '{round_name}' not available for year {year}, grade '{grade_value}'. Available: {available_rounds}")
                    return None

                self.page.select_option(round_selector, round_name)
                self.page.wait_for_load_state('networkidle', timeout=timeout)
                
                time.sleep(delay)

                html_content = self.page.content()
                self.logger.info(f"Successfully retrieved HTML for {year}, grade '{grade_value}', round '{round_name}'")
                return html_content

            except Exception as e:
                self.logger.warning(
                    f"An error occurred on attempt {attempt + 1} for {year}, grade '{grade_value}', round '{round_name}': {e}"
                )
                if attempt + 1 == max_retries:
                    self.logger.error(
                        f"Failed to get HTML for {year}, grade '{grade_value}', round '{round_name}' after {max_retries} attempts."
                    )
                    return None
        return None
