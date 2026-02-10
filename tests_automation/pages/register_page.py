import logging
from playwright.sync_api import Page

from tests_automation.utils.config import Config
from tests_automation.pages.base_page import BasePage
from tests_automation.utils.common_helper import mask_text
from tests_automation.models.data_models import AccountRegisterData

logger = logging.getLogger(__name__)

class AccountRegisterPage(BasePage):

    URL = f"{Config.BASE_URL}/register"

    def __init__(self, page: Page) -> None:
        self.page = page

        self.email_input = self.page.get_by_role("textbox", name="Email Address")
        self.password_input = self.page.get_by_role("textbox", name="Password", exact=True)
        self.confirm_password = self.page.get_by_role("textbox", name="Confirm Password")
        self.register_button = self.page.get_by_role("button", name="Register")
        self.login_here_link = self.page.get_by_role("link", name="Log In here.")

    def enter_email(self, email: str) -> None:
        logger.info(f"[INPUT] Entering email address: '{email}'...")
        self.email_input.fill(email)
        logger.info("[SUCCESS] Email address entered.")

    def enter_password(self, password: str) -> None:
        logger.info(f"[INPUT] Entering password: '{mask_text(password)}'...")
        logger.debug(f"[DEBUG-DATA] Entering password: {password}...")
        self.password_input.fill(password)
        logger.info("[SUCCESS] Password entered.")

    def click_register_button(self) -> None:
        logger.info("[ACTION] Clicking 'Register' button...")
        self.register_button.click()
        logger.info("[SUCCESS] 'Register' button clicked.")

    def register_account(self, user_data: AccountRegisterData) -> None:
        logger.info(f"[ACTION] Registering account for email: '{user_data.email}'...")

        self.enter_email(user_data.email)
        self.enter_password(user_data.password)
        self.register_button.click()

        logger.info("[SUCCESS] Registration sequence completed.")

