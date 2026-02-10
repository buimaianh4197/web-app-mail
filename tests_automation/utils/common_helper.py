import logging

logger = logging.getLogger(__name__)

def mask_text(text: str) -> str:
    return "*" * len(text) if text else ""