import re
import json
import allure
import logging
import requests
from typing import Optional
from dataclasses import asdict

from tests_automation.utils.config import Config
from tests_automation.models.data_models import LoginData, AccountRegisterData, EmailData

logger = logging.getLogger(__name__)

class MailAPIClient:

    def __init__(self) -> None:
        self.base_url = Config.BASE_URL
        self.session = requests.Session() 
        logger.info(f"[API][CONFIG] Initialized MailAPIClient with Base URL: '{self.base_url}'.")

    def mask_text(self, text: str) -> str:
        return "*" * len(str(text)) if text else ""

    def _attach_curl(self, req: requests.PreparedRequest) -> str:
        logger.debug(f"[ALLURE][ATTACH] Generating CURL command for: {req.method} {req.url}")
        
        command = f"curl -X {req.method} '{req.url}'"
        for k, v in req.headers.items():
            command += f" \\\n  -H '{k}: {v}'"
        
        body_str = "None"
        if req.body:
            body_str = req.body.decode('utf-8') if isinstance(req.body, bytes) else str(req.body)
            if "password" in body_str:
                logger.debug("[ALLURE][SECURITY] Masking sensitive data in CURL body...")
                body_str = re.sub(
                    r'("password":\s*")([^"]+)(")', 
                    lambda m: f"{m.group(1)}{self.mask_text(m.group(2))}{m.group(3)}", 
                    body_str
                )
            command += f" \\\n  -d '{body_str}'"
        
        allure.attach(
            command, 
            name="Debug_Request_CURL", 
            attachment_type=allure.attachment_type.TEXT
        )
        logger.info("[ALLURE][SUCCESS] Attached 'Debug_Request_CURL' to Allure.")
        return body_str

    def _attach_request_details(self, req: requests.PreparedRequest, masked_body: str) -> None:
        logger.debug(f"[ALLURE][ATTACH] Formatting Request Payload for Allure...")
        
        request_info = {
            "Method": req.method,
            "URL": req.url,
            "Headers": dict(req.headers),
            "Body": masked_body
        }

        request_data = json.dumps(request_info, indent=4, ensure_ascii=False)
        allure.attach(
            request_data, 
            name="Data_Request_Payload", 
            attachment_type=allure.attachment_type.JSON
        )
        logger.info("[ALLURE][SUCCESS] Attached 'Data_Request_Payload' to Allure.")

    def _attach_response_details(self, response: requests.Response) -> None:
        logger.debug(f"[ALLURE][ATTACH] Processing Response from {response.url} (Status: {response.status_code})...")
        
        try:
            response_json = response.json()
            response_display = json.dumps(response_json, indent=4, ensure_ascii=False)
            type_allure = allure.attachment_type.JSON
            logger.debug("[ALLURE][FORMAT] Response identified as JSON.")
        except Exception:
            response_display = response.text
            type_allure = allure.attachment_type.TEXT
            logger.debug("[ALLURE][FORMAT] Response identified as Raw Text/HTML.")

        res_info = (
            f"Status: {response.status_code} {response.reason}\n"
            f"Elapsed: {response.elapsed.total_seconds()}s\n\n"
            f"Headers: {json.dumps(dict(response.headers), indent=4)}\n\n"
            f"Body:\n{response_display}"
        )
        
        allure.attach(
            res_info, 
            name=f"Data_Response_{response.status_code}", 
            attachment_type=type_allure
        )
        logger.info(f"[ALLURE][SUCCESS] Attached 'Data_Response_{response.status_code}' to Allure.")

    def _attach_full_api_trace(self, response: requests.Response) -> None:
        request = response.request
        masked_body = self._attach_curl(request)
        self._attach_request_details(request, masked_body)
        self._attach_response_details(response)
        
        logger.debug(f"[ALLURE][SUCCESS] Full HTTP trace attached to Allure for '{request.url}'.")

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        method = method.upper()
        
        if method in ["POST", "PUT", "DELETE", "PATCH"]:
            token = self.session.cookies.get('csrftoken')
            if not token:
                logger.debug(f"[API][WAIT] No CSRF token found in cookies. Fetching from '/login'...")
                self._get_csrf_token()
                token = self.session.cookies.get('csrftoken')

            if token:
                kwargs.setdefault("headers", {})["X-CSRFToken"] = token
                logger.debug(f"[API][ACTION] Injecting X-CSRFToken for {method} request...")
            else:
                logger.error(f"[API][ERROR] CSRF token missing for {method} '{path}'.")
        else:
            logger.debug(f"[API][CONFIG] Using standard {method} request.")

        try:
            response = self.session.request(method, url, **kwargs)
            
            self._attach_full_api_trace(response)
            
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            self._attach_full_api_trace(response)
            logger.error(f"[API][ERROR] {method} {path} | Status: {response.status_code}")
            logger.error(f"[API][RESPONSE_BODY]: {response.text}")
            raise
        except Exception as e:
            logger.error(f"[API][ERROR] System failure during {method} '{path}': {e}")
            raise

    def _get_csrf_token(self, path: str = "/login") -> Optional[str]:
        logger.debug(f"[API][ACTION] Fetching CSRF token from '{path}'...")
        self._request("GET", path)
        token = self.session.cookies.get('csrftoken')
        logger.debug(f"[API][SUCCESS] CSRF token obtained.")
        return token

    def register(self, user_data: AccountRegisterData) -> requests.Response | None:
        logger.info(f"[API][ACTION] Registering account with email: '{user_data.email}'...")
        data = asdict(user_data)
        headers = {"Referer": f"{self.base_url}/register"}
        response = self._request("POST", "/register", data=data, headers=headers)
        logger.info(f"[API][SUCCESS] Registration completed for '{user_data.email}'. Status: {response.status_code}.")
        return response

    def login(self, user_data: LoginData) -> requests.Response | None:
        logger.info(f"[API][ACTION] Logging in as: '{user_data.email}'...")
        data = asdict(user_data)
        headers = {"Referer": f"{self.base_url}/login"}
        response = self._request("POST", "/login", data=data, headers=headers)
        logger.info(f"[API][SUCCESS] Login attempt finished for '{user_data.email}'. Status: {response.status_code}.")
        return response

    def logout(self) -> requests.Response | None:
        logger.info("[API][ACTION] Logging out...")
        response = self._request("GET", "/logout")
        logger.info("[API][SUCCESS] Logged out.")
        return response

    def send_email(self, email_data: EmailData) -> requests.Response | None:
        logger.info(f"[API][ACTION] Sending email to '{email_data.recipients}'...")
        payload = asdict(email_data)
        headers = {"Referer": f"{self.base_url}/"}
        response = self._request("POST", "/emails", json=payload, headers=headers)
        logger.info(f"[API][SUCCESS] Email sent to '{email_data.recipients}'.")
        return response

    def get_mailbox(self, mailbox: str = "inbox") -> requests.Response | None:
        logger.info(f"[API][ACTION] Fetching mailbox: '{mailbox}'...")
        response = self._request("GET", f"/emails/{mailbox}")
        logger.info(f"[API][SUCCESS] Mailbox '{mailbox}' retrieved.")
        return response

    def update_email_status(self, 
        email_id: int, 
        read: Optional[bool] = None, 
        archived: Optional[bool] = None
    ) -> requests.Response | None:
        
        payload = {}
        if read is not None:
            payload["read"] = read
        if archived is not None:
            payload["archived"] = archived

        log_details = [f"{key}={value}" for key, value in payload.items()]
        log_message = ", ".join(log_details)

        logger.info(f"[API][ACTION] Updating email ID '{email_id}' with: {log_message}")
        
        response = self._request(
            method="PUT", 
            path=f"/emails/{email_id}", 
            json=payload
        )
        
        logger.info(f"[API][SUCCESS] Status for email ID '{email_id}' updated successfully.")
        return response