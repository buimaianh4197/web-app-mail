import time
import allure
import logging
from pytest_check.context_manager import check

from tests_automation.models.data_models import LoginData
from tests_automation.models.data_models import EmailData
from tests_automation.utils.api_client import MailAPIClient
from tests_automation.models.data_models import AccountRegisterData
from tests_automation.schemas.email_schema import (
    EmailDetailSchema, 
    EmailComposeSchema, 
    ErrorEmailComposeSchema, 
    ErrorEmailDetailsSchema
)
from tests_automation.resources.api.constants import (
    InvalidMailboxResponse, 
    MissingRecipientResponse, 
    NotExistentUserResponse, 
    NotExistentEmailResponse, 
    SuccessComposeEmailResponse
)

logger = logging.getLogger(__name__)

class TestMailbox:
    def test_compose_mail_with_valid_payload(
            self, 
            api_client: MailAPIClient, 
            clean_db
        ):

        # Prepare data
        sender_email = f"user_{int(time.time())}@test.com"
        sender_password = "123456"

        recipient_email = f"user_{int(time.time())}@test.com"
        recipient_password = "123456"

        email_subject = "[TC-001] Test compose email with valid payload"
        email_body = "Verify status code, response body, 'sent' mailbox of sender, 'inbox' mailbox of recipient"
        
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

        login_sender_data = LoginData(
            email=sender_email, 
            password=sender_password
        )

        email_payload = EmailData(
            recipients=recipient_email,
            subject=email_subject,
            body=email_body
        )

        api_client.register(sender_user_data)
        api_client.register(recipient_user_data)
        api_client.login(login_sender_data)

        # Execute test
        with allure.step(f"Compose email from {sender_email} to {recipient_email}"):
            compose_email_response = api_client.compose_email(email_payload)
            compose_email_res_body = compose_email_response.json()

        with allure.step(f"Verify actual resuslts:"):
            with allure.step("Verify response of the compose email api:"):
                with allure.step(f"Verify if status code is '{SuccessComposeEmailResponse.STATUS_CODE}'"):
                    with check:
                        assert compose_email_response.status_code == SuccessComposeEmailResponse.STATUS_CODE
                with allure.step(f"Verify if schema follows 'EmailComposeSchema' class"):
                    with check:
                        EmailComposeSchema.model_validate(compose_email_res_body)
                with allure.step(f"Verify if response body's content is a success message"):
                    with check:
                        assert compose_email_res_body.get("message") == SuccessComposeEmailResponse.MESSAGE
            
            with allure.step(f"Verify sender's 'sent' mailbox:"):
                get_sent_mailbox_response = api_client.get_mailbox("sent")
                get_sent_mailbox_res_body = get_sent_mailbox_response.json()
                with allure.step(f"Verify if status code is '200'"):
                    with check:
                        assert compose_email_response.status_code == 201
                with allure.step(f"Verify if schema follows 'EmailComposeSchema' class"):
                    with check:
                        EmailComposeSchema.model_validate(compose_email_res_body)

        # 1. Gửi email với dữ liệu hợp lệ
        # Chuẩn bị: 
        # - Tạo một tài khoản người dùng mới chưa tồn tại trong hệ thống: user_str(time())@gmail.com, 123456
        # - Đăng nhập bằng tài khoản đó: user_str(time())@gmail.com, 123456

        # Test:
        # - POST /emails, 
        # headers={"X-CSRFToken": "csrftoken"}, 
        # data={"recipients": "", "subject": "", "body": ""}

        # Verify:

        # - Response:
        # + status code: 201
        # + message: {"message": "Email sent successfully."}

        # - Sender's sent mailbox state: 
        # GET /emails/sent
        # + status code: 200
        # + Tìm email có timestamp mới nhất
        # + Kiểm tra schema
        # + Kiểm tra nội dung mail đó có giống mail vừa gửi không
        # + Kiểm tra read là true, archived là false, timestamp đúng format, timezone

        # - recipients' inbox mailbox state
        # + Đăng nhập vào tài khoản của các người nhận
        # + GET /emails/inbox
        # + status code: 200
        # + Tìm email có timestamp mới nhất
        # + Kiểm tra schema
        # + kiểm tra nội dung mail đó có giống mail vừa gửi không
        # + kiểm tra read là false, archived là false, timestamp đúng format, timezone

        # Clean registered account and composed email from DB
