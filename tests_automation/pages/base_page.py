import logging
from playwright.sync_api import Page, Locator

logger = logging.getLogger(__name__)

class BasePage:

    URL = ""
    
    def __init__(self, page: Page) -> None:
        self.page = page

    def navigate(self) -> None:
        logger.info(f"[ACTION] Navigating to URL: '{self.URL}'...")
        self.page.goto(self.URL)
        logger.info(f"[SUCCESS] Navigation to URL: '{self.URL}' completed.")