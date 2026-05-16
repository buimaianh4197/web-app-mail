import os
import allure
import pytest
import shutil
import django
import logging
import platform
from pathlib import Path
from typing import Generator
from dataclasses import asdict
from _pytest.nodes import Item
from playwright.sync_api import Page

from tests_automation.utils.config import Config
from tests_automation.pages.login_page import LoginPage
from tests_automation.utils.db_handler import DBHandler
from tests_automation.pages.mailbox_page import MailboxPage
from tests_automation.utils.api_client import MailAPIClient
from tests_automation.pages.register_page import AccountRegisterPage

logger = logging.getLogger(__name__)

@pytest.fixture()
def api_client():
    logger.debug("[SETUP] Initializing 'MailAPIClient' fixture.")
    yield MailAPIClient()

@pytest.fixture()
def db_handler():
    logger.debug("[SETUP] Initializing 'DBHandler' fixture.")
    db_handler = DBHandler()
    # db_handler.reset_test_data()
    yield db_handler
    db_handler.reset_test_data()

@pytest.fixture()
def account_register_page(page: Page):
    logger.debug("[SETUP] Initializing 'AccountRegisterPage' fixture.")
    yield AccountRegisterPage(page)

@pytest.fixture()
def mailbox_page(page: Page):
    logger.debug("[SETUP] Initializing 'MailboxPage' fixture.")
    yield MailboxPage(page)

@pytest.fixture()
def login_page(page: Page):
    logger.debug("[SETUP] Initializing 'LoginPage' fixture.")
    yield LoginPage(page)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: Item, call: pytest.CallInfo) -> Generator:
    outcome = yield
    report = outcome.get_result()

    page = None
    funcargs = getattr(item, "funcargs", {})
    if "page" in funcargs:
        page = funcargs["page"]
    else:
        for fixture_value in funcargs.values():
            if hasattr(fixture_value, "page") and isinstance(fixture_value.page, Page):
                page = fixture_value.page
                break
    
    if not page:
        logger.debug(f"[ALLURE][DEBUG] No Playwright page object found for test: {item.name}.")

    if report.when == "call":
        item.test_failed = report.failed
        status = "PASSED" if report.passed else "FAILED"
        
        if report.passed:
            logger.info(f"[REPORT][EVENT] --- TEST PASSED: {item.name} ---")
        else:
            logger.error(f"[REPORT][EVENT] --- TEST FAILED: {item.name} ---")
            
            if hasattr(report.longrepr, "reprcrash"):
                msg = f"{report.longrepr.reprcrash.message} (at {report.longrepr.reprcrash.path}:{report.longrepr.reprcrash.lineno})"
            else:
                msg = str(report.longrepr)

            logger.error(f"[REPORT][ERROR] Reason: {msg}.")

        if page:
            try:
                logger.info(f"[ALLURE][ACTION] Capturing {status} screenshot...")
                allure.attach(
                    page.screenshot(full_page=True, animations="disabled"),
                    name=f"Screenshot_{status}_Call",
                    attachment_type=allure.attachment_type.PNG
                )
                logger.info(f"[ALLURE][SUCCESS] Screenshot attached to Allure.")
            except Exception as e:
                logger.warning(f"[ALLURE][WARNING] Could not capture screenshot: {e}.")

    if report.when == "teardown":
        is_failed = getattr(item, "test_failed", False)
        
        if is_failed:
            logger.info(f"[ALLURE][ACTION] Test FAILED. Searching for Trace and Video artifacts...")
            
            output_dir = Path(item.config.getoption("--output") or "test-results")
            if not output_dir.exists():
                logger.error(f"[ALLURE][ERROR] Artifacts directory not found: {output_dir}.")
                return

            test_method_name = item.name.split('[')[0]
            found_folder = False

            for entry in output_dir.iterdir():
                if entry.is_dir() and test_method_name in entry.name.replace("-", "_"):
                    found_folder = True
                    logger.debug(f"[ALLURE][DEBUG] Matching artifact folder found: {entry.name}.")
                    
                    trace_file = entry / "trace.zip"
                    if trace_file.exists():
                        logger.info(f"[ALLURE][ATTACH] Attaching Trace file: {trace_file}.")
                        allure.attach.file(str(trace_file), name="Log_Error_Trace", attachment_type=allure.attachment_type.ZIP)
                    else:
                        logger.debug(f"[ALLURE][DEBUG] Trace file not found in {entry}.")

                    video_file = entry / "video.webm"
                    if video_file.exists():
                        logger.info(f"[ALLURE][ATTACH] Attaching Video file: {video_file}.")
                        allure.attach.file(str(video_file), name="Log_Error_Video", attachment_type=allure.attachment_type.WEBM)
                    else:
                        logger.debug(f"[ALLURE][DEBUG] Video file not found in {entry}.")
            
            if not found_folder:
                logger.warning(f"[ALLURE][WARNING] No artifact folder found for test: {test_method_name}.")
        else:
            logger.info(f"[ALLURE][EVENT] Test PASSED. Skipping Trace and Video attachments.")

def create_environment_properties(allure_dir: Path) -> None:
    env_file = allure_dir / "environment.properties"
    
    logger.info(f"[ALLURE][ACTION] Generating Allure environment properties at: {env_file}...")
    
    lines = [
        f"Base_URL={Config.BASE_URL}",
        f"Browser={Config.BROWSER.capitalize()}",
        f"OS_Platform={platform.system()} {platform.release()}",
        f"Python_Version={platform.python_version()}",
        f"Django_Version={django.get_version()}",
        f"Executed_On={'GitHub Actions' if os.getenv('GITHUB_ACTIONS') else 'Local Machine'}"
    ]
    
    try:
        env_file.write_text("\n".join(lines), encoding="utf-8")
        logger.info(f"[ALLURE][SUCCESS] Environment properties created successfully.")
    except Exception as e:
        logger.error(f"[ALLURE][ERROR] Failed to create environment.properties: {e}.")

def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    logger.info("[ALLURE][EVENT] --- Pytest session finishing. Starting Allure artifact collection ---")
    
    allure_option = session.config.getoption('--alluredir')
    if not allure_option:
        logger.warning("[ALLURE][WARNING] Allure directory not specified (--alluredir). Skipping artifact collection.")
        return

    allure_dir = Path(allure_option).resolve()
    
    if allure_dir.exists():
        create_environment_properties(allure_dir)
        
        resources_dir = Path(__file__).resolve().parent.parent / "resources"
        source_categories = resources_dir / "categories.json"
        target_categories = allure_dir / "categories.json"
        
        if source_categories.exists():
            try:
                logger.info(f"[ALLURE][ACTION] Copying categories.json to {allure_dir}...")
                shutil.copyfile(source_categories, target_categories)
                logger.info(f"[ALLURE][SUCCESS] Categories file attached to report results.")
            except Exception as e:
                logger.error(f"[ALLURE][ERROR] Failed to copy categories file: {e}.")
        else:
            logger.warning(f"[ALLURE][WARNING] categories.json not found at: {source_categories}. Report will lack custom defect categorization.")
    else:
        logger.error(f"[ALLURE][ERROR] Allure results directory does not exist: {allure_dir}.")

    exit_codes = {
        0: "ALL TESTS PASSED",
        1: "TESTS FAILED",
        2: "INTERRUPTED BY USER",
        3: "INTERNAL ERROR",
        4: "USAGE ERROR",
        5: "NO TESTS COLLECTED"
    }
    status_text = exit_codes.get(exitstatus, f"UNKNOWN ERROR (Code: {exitstatus})")
    logger.info(f"[TEST][EVENT] --- Session finished with status: {status_text} ---")