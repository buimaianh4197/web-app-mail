import logging
from playwright.sync_api import Page

from tests_automation.utils.config import Config
from tests_automation.pages.base_page import BasePage
from tests_automation.models.data_models import EmailData

logger = logging.getLogger(__name__)

class MailboxPage(BasePage):

    URL = Config.BASE_URL
    
    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.heading = self.page.get_by_role("heading", name="maihoa@gmail.com")
        self.inbox_button = self.page.get_by_role("button", name="Inbox")
        self.compose_button = self.page.get_by_role("button", name="Compose")
        self.sent_button = self.page.get_by_role("button", name="Sent")
        self.archived_button = self.page.get_by_role("button", name="Archived")
        self.logout_button = self.page.get_by_role("link", name="Log Out")
        
        self.sender_email_input = self.page.get_by_role("textbox").first
        self.recipients_email_input = self.page.locator("#compose-recipients")
        self.subject_input = self.page.get_by_role("textbox", name="Subject")
        self.body_textarea = self.page.get_by_role("textbox", name="Body")
        self.submit_button = self.page.get_by_role("button", name="Submit")

        self.archive_button = self.page.get_by_role("button", name="Archive")
        self.unarchive_button = self.page.get_by_role("button", name="Unarchive")
        self.reply_button = self.page.get_by_role("button", name="Reply")

    def click_inbox_button(self) -> None:
        logger.info("[ACTION] Clicking 'Inbox' button...")
        self.inbox_button.click()
        logger.info("[SUCCESS] 'Inbox' button clicked.")

    def click_compose_button(self) -> None:
        logger.info("[ACTION] Clicking 'Compose' button...")
        self.compose_button.click()
        logger.info("[SUCCESS] 'Compose' button clicked.")

    def click_sent_button(self) -> None:
        logger.info("[ACTION] Clicking 'Sent' button...")
        self.sent_button.click()
        logger.info("[SUCCESS] 'Sent' button clicked.")

    def click_archived_button(self) -> None:
        logger.info("[ACTION] Clicking 'Archived' navigation button...")
        self.archived_button.click()
        logger.info("[SUCCESS] 'Archived' navigation button clicked.")

    def click_logout_button(self) -> None:
        logger.info("[ACTION] Clicking 'Log Out' link...")
        self.logout_button.click()
        logger.info("[SUCCESS] 'Log Out' link clicked.")

    def click_archive_action(self) -> None:
        logger.info("[ACTION] Clicking 'Archive' button...")
        self.archive_button.click()
        logger.info("[SUCCESS] 'Archive' button clicked.")

    def click_unarchive_button(self) -> None:
        logger.info("[ACTION] Clicking 'Unarchive' button...")
        self.unarchive_button.click()
        logger.info("[SUCCESS] 'Unarchive' button clicked.")

    def click_reply_button(self) -> None:
        logger.info("[ACTION] Clicking 'Reply' button...")
        self.reply_button.click()
        logger.info("[SUCCESS] 'Reply' button clicked.")

    def enter_sender_email(self, email: str) -> None:
        logger.info(f"[INPUT] Entering sender email: '{email}'...")
        self.sender_email_input.fill(email)
        logger.info("[SUCCESS] Sender email entered.")

    def enter_recipients_email(self, email: str) -> None:
        logger.info(f"[INPUT] Entering recipients email: '{email}'...")
        self.recipients_email_input.fill(email)
        logger.info("[SUCCESS] Recipients email entered.")

    def enter_subject(self, subject: str) -> None:
        logger.info(f"[INPUT] Entering subject: '{subject}'...")
        self.subject_input.fill(subject)
        logger.info("[SUCCESS] Subject entered.")

    def enter_body_content(self, body_text: str) -> None:
        logger.info(f"[INPUT] Entering body content...")
        self.body_textarea.fill(body_text)
        logger.info("[SUCCESS] Body content entered.")

    def click_submit_button(self) -> None:
        logger.info("[ACTION] Clicking 'Submit' button...")
        self.submit_button.click()
        logger.info("[SUCCESS] 'Submit' button clicked.")

    def send_email(self, email_data: EmailData) -> None:
        logger.info(f"[ACTION] Starting send email sequence to: '{email_data.recipients}'...")

        self.enter_recipients_email(email_data.recipients)
        self.enter_subject(email_data.subject)
        self.enter_body_content(email_data.body)
        
        self.click_submit_button()

        logger.info(f"[SUCCESS] Email sent successfully to '{email_data.recipients}'.")

    