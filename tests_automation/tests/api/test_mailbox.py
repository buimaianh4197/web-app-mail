import time
import allure
import logging
from pytest_check.context_manager import check

from tests_automation.models.data_models import LoginData
from tests_automation.models.data_models import EmailData
from tests_automation.utils.db_handler import DBHandler
from tests_automation.utils.api_client import MailAPIClient
from tests_automation.models.data_models import AccountRegisterData
from tests_automation.schemas.email_schema import (
    EmailListSchema,
    EmailDetailSchema, 
    EmailComposeSchema, 
    ErrorEmailComposeSchema, 
    ErrorEmailDetailsSchema 
)
from tests_automation.resources.api.constants import (
    InvalidMailboxResponse, 
    NotExistentUserResponse, 
    MissingRecipientResponse, 
    NotExistentEmailResponse, 
    SuccessGetMailboxResponse,
    SuccessComposeEmailResponse
)

logger = logging.getLogger(__name__)

class TestMailbox:
    def test_compose_mail_with_valid_payload(
            self, 
            api_client: MailAPIClient, 
            db_handler: DBHandler
        ):

        # Prepare data
        sender_email = f"user_{int(time.time())}@test.com"
        sender_password = "123456"

        recipient_email = f"user_{int(time.time())}@test.com"
        recipient_password = "123456"

        email_subject = "[TC-001] Test compose email with valid payload"
        email_body = "Verify status code, response body, database, 'sent' mailbox of sender, 'inbox' mailbox of recipient"
        
        sender_user_data = AccountRegisterData(
            email=sender_email, 
            password=sender_password, 
            confirm_password=sender_password
        )

        recipient_user_data = AccountRegisterData(
            email=recipient_email, 
            password=recipient_password, 
            confirm_password=recipient_password
        )

        sender_login_data = LoginData(
            email=sender_email, 
            password=sender_password
        )

        recipient_login_data = LoginData(
            email=recipient_email, 
            password=recipient_password
        )

        email_payload = EmailData(
            recipients=recipient_email,
            subject=email_subject,
            body=email_body
        )

        sent_expected_values = {
            "sender": sender_email,
            "recipients": email_payload.recipients,
            "subject": email_payload.subject,
            "body": email_payload.body,
            "read": True,
            "archived": False
        }

        inbox_expected_values = {
            "sender": sender_email,
            "recipients": email_payload.recipients,
            "subject": email_payload.subject,
            "body": email_payload.body,
            "read": False,
            "archived": False
        }

        api_client.register(sender_user_data)
        api_client.register(recipient_user_data)
        api_client.login(sender_login_data)

        # Execute test
        with allure.step(f"Compose email from {sender_email} to {recipient_email}"):
            compose_email_response = api_client.compose_email(email_payload)
            compose_email_response_body = compose_email_response.json()

        with allure.step(f"Verify actual resuslts:"):
            with allure.step("Verify response of the compose email api:"):
                with allure.step(f"Verify if status code is '{SuccessComposeEmailResponse.STATUS_CODE}'"):
                    with check:
                        assert compose_email_response.status_code == SuccessComposeEmailResponse.STATUS_CODE
                with allure.step(f"Verify if schema follows 'EmailComposeSchema' class"):
                    with check:
                        EmailComposeSchema.model_validate(compose_email_response_body)
                with allure.step(f"Verify if response body's content is a success message"):
                    with check:
                        assert compose_email_response_body.get("message") == SuccessComposeEmailResponse.MESSAGE

            with allure.step(f"Verify state of the database:"):
                # user_id = SELECT id FROM auth_user WHERE email=sender_email
                # db_latest_sent_email_info = SELECT id, subject, body, read, archived, timestamp FROM mail_email WHERE user_id=user_id AND sender_id=user_id ODER BY timestamp DESC LIMIT 1
                # db_email_id = db_email_info["id"]
                # db_recipient_ids = SELECT user_id FROM mail_email_recipients WHERE email_id=db_email_id
                # db_recipient_emails = SELECT email FROM auth_user WHERE id IN db_recipient_ids
                # db_latest_sent_email_info_dict = {
                # "sender": sender_email,
                # "recipients": db_recipient_emails,
                # "subject": db_email_info["subject"],
                # "body": db_email_info["body"],
                # "read": db_email_info["read"],
                # "archived": db_email_info["archived"],
                #}
                if latest_db_mail:
                    for field, expected_value in sent_expected_values.items():
                        with check:
                            assert latest_db_mail[field] == expected_value, f"Failed on field: {field}"
            
            with allure.step(f"Verify sender's 'sent' mailbox:"):
                get_sent_mailbox_response = api_client.get_mailbox("sent")
                get_sent_mailbox_response_body = get_sent_mailbox_response.json()
                with allure.step(f"Verify if status code is '{SuccessGetMailboxResponse.STATUS_CODE}'"):
                    with check:
                        assert get_sent_mailbox_response.status_code == SuccessGetMailboxResponse.STATUS_CODE
                with allure.step(f"Verify if schema follows 'EmailListSchema' class"):
                    with check:
                        EmailListSchema.model_validate(get_sent_mailbox_response_body)
                with allure.step(f"Verify if the first mail is the email which the sender has already sent"):
                    latest_sent_mail = get_sent_mailbox_response_body[0]
                    for field, expected_value in sent_expected_values.items():
                        with check:
                            assert latest_sent_mail[field] == expected_value, f"Failed on field: {field}"

            with allure.step(f"Verify recipients' 'inbox' mailbox:"):
                api_client.logout()
                api_client.login(recipient_login_data)
                get_inbox_mailbox_response = api_client.get_mailbox("inbox")
                get_inbox_mailbox_response_body = get_inbox_mailbox_response.json()
                with allure.step(f"Verify if status code is '{SuccessGetMailboxResponse.STATUS_CODE}'"):
                    with check:
                        assert get_inbox_mailbox_response.status_code == SuccessGetMailboxResponse.STATUS_CODE
                with allure.step(f"Verify if schema follows 'EmailListSchema' class"):
                    with check:
                        EmailListSchema.model_validate(get_inbox_mailbox_response_body)
                with allure.step(f"Verify if the first mail is the email which the sender has already sent"):
                    latest_inbox_mail = get_inbox_mailbox_response_body[0]
                    for field, expected_value in inbox_expected_values.items():
                        with check:
                            assert latest_inbox_mail[field] == expected_value, f"Failed on field: {field}"

