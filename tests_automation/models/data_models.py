import json
from dataclasses import asdict
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BaseData:
    def mask_data(self) -> str:
        data = asdict(self)
        for key in data:
            if "password" in key.lower():
                data[key] = "*" * len(str(data[key]))
        masked_data = json.dumps(data, indent=2)
        return masked_data

@dataclass
class AccountRegisterData(BaseData):
    email: str
    password: str
    confirm_password: str

@dataclass
class LoginData(BaseData):
    email: str
    password: str

@dataclass
class EmailData:
    recipients: str
    subject: str
    body: str