import logging
from playwright.sync_api import Page

from tests_automation.utils.config import Config
from tests_automation.pages.base_page import BasePage
from tests_automation.models.data_models import LoginData
from tests_automation.utils.common_helper import mask_text

logger = logging.getLogger(__name__)

class LoginPage(BasePage):

    URL = f"{Config.BASE_URL}/login"
    
    def __init__(self, page: Page) -> None:
        super().__init__(page)
    
        self.email_input = self.page.get_by_role("textbox", name="Email")
        self.password_input = self.page.get_by_role("textbox", name="Password")
        self.login_button = self.page.get_by_role("button", name="Login")
        self.register_here_link = self.page.get_by_role("link", name="Register here.")

    def enter_email(self, email: str) -> None:
        logger.info(f"[INPUT] Entering email: '{email}'...")
        self.email_input.fill(email)
        logger.info("[SUCCESS] Email entered.")

    def enter_password(self, password: str) -> None:
        logger.info(f"[INPUT] Entering password: '{mask_text(password)}'...")
        logger.debug(f"[DEBUG-DATA] Entering password: {password}...")
        self.password_input.fill(password)
        logger.info("[SUCCESS] Password entered.")

    def click_login_button(self) -> None:
        logger.info("[ACTION] Clicking 'Login' button...")
        self.login_button.click()
        logger.info("[SUCCESS] 'Login' button clicked.")

    def login(self, login_data: LoginData) -> None:
        logger.info(f"[ACTION] Performing full login sequence for: '{login_data.email}'...")

        self.enter_email(login_data.email)
        self.enter_password(login_data.password)
        self.click_login_button()

        logger.info("[SUCCESS] Login sequence completed.")

    def click_register_here_link(self) -> None:
        logger.info("[ACTION] Clicking 'Register here' link...")
        self.register_here_link.click()
        logger.info("[SUCCESS] 'Register here' link clicked.")