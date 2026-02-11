class SuccessComposeEmailResponse:
    STATUS_CODE = 201
    MESSAGE = "Email sent successfully."

class SuccessGetMailboxResponse:
    STATUS_CODE = 200

class InvalidMailboxResponse:
    STATUS_CODE = 400
    ERROR = "Invalid mailbox."

class NotExistentEmailResponse:
    STATUS_CODE = 404
    ERROR = "Email not found."

class MissingRecipientResponse:
    STATUS_CODE = 400
    ERROR = "At least one recipient required."

class NotExistentUserResponse:
    STATUS_CODE = 400
    # expected_msg = NotExistentUserResponse.ERROR_TEMPLATE.format(email=test_email)
    ERROR_TEMPLATE = "User with email {email} does not exist."