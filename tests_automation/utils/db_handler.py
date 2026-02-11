import sqlite3
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from tests_automation.utils.config import Config

logger = logging.getLogger(__name__)

class DBHandler:

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Config.DB_DIR
        logger.info(f"[DB][CONFIG] Initialized DBHandler with path: '{self.db_path}'.")

    def _execute_query(
            self, 
            query: str, 
            params: tuple = (), 
            is_select: bool = True
        ) -> Any:
        
        if not self.db_path.exists():
            logger.error(f"[DB][ERROR] Database file not found at '{self.db_path}'.")
            return None

        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            logger.debug(f"[DB][EXECUTE] Query: {query} | Params: {params}")
            cursor.execute(query, params)
            
            if is_select:
                return [dict(row) for row in cursor.fetchall()]
            else:
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"[DB][ERROR] Query failed: {e}.")
            return None
        finally:
            conn.close()

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        logger.info(f"[DB][ACTION] Fetching user by email: '{email}'...")
        
        query = "SELECT id, email FROM auth_user WHERE email = ?"
        result = self._execute_query(query, (email,))
        
        if result:
            logger.info(f"[DB][SUCCESS] User found with email: '{email}'.")
            return result[0]
        logger.warning(f"[DB][WARNING] No user found with email: '{email}'.")
        return None

    def is_user_exists(self, email: str) -> bool:
        logger.info(f"[DB][VERIFICATION] Checking if user exists: '{email}'...")
        exists = self.get_user_by_email(email) is not None
        logger.info(f"[DB][SUCCESS] User existence check for '{email}': {exists}.")
        return exists

    def get_latest_email_for_user(self, owner_email: str) -> Optional[Dict[str, Any]]:
        logger.info(f"[DB][ACTION] Getting latest email for user: '{owner_email}'...")
        
        query = """
            SELECT m.* FROM mail_email m
            JOIN auth_user u ON m.user_id = u.id
            WHERE u.email = ?
            ORDER BY m.timestamp DESC LIMIT 1
        """
        result = self._execute_query(query, (owner_email,))
        
        if result:
            logger.info(f"[DB][SUCCESS] Latest email retrieved for user: '{owner_email}'.")
            return result[0]
        logger.warning(f"[DB][WARNING] No emails found for user: '{owner_email}'.")
        return None

    def get_email_count_by_subject(self, subject_pattern: str) -> int:
        logger.info(f"[DB][ACTION] Counting emails with subject matching: '{subject_pattern}'...")
        
        query = "SELECT COUNT(*) as total FROM mail_email WHERE subject LIKE ?"
        result = self._execute_query(query, (f"%{subject_pattern}%",))
        count = result[0]['total'] if result else 0
        
        logger.info(f"[DB][SUCCESS] Found {count} emails matching subject: '{subject_pattern}'.")
        return count

    def delete_user_by_email(self) -> int:
        logger.info(f"[DB][ACTION] Deleting test user with pattern: '%@test.com'...")
        
        query = "DELETE FROM auth_user WHERE email LIKE '%@test.com'"
        count = self._execute_query(query, is_select=False)
        
        logger.info(f"[DB][SUCCESS] Deleted {count} user(s) with pattern: '%@test.com'.")
        return count

    def reset_test_data(self) -> int:
        logger.info("[DB][ACTION] Resetting all test data (domain '@test.com')...")
        
        query_emails = "DELETE FROM mail_email WHERE user_id IN (SELECT id FROM auth_user WHERE email LIKE '%@test.com')"
        query_users = "DELETE FROM auth_user WHERE email LIKE '%@test.com'"
        
        self._execute_query(query_emails, is_select=False)
        count = self._execute_query(query_users, is_select=False)
        
        logger.info(f"[DB][SUCCESS] Cleanup finished. '{count}' test users and their emails removed.")
        return count

    def get_recipients_of_email(self, email_id: int) -> List[str]:
        logger.info(f"[DB][ACTION] Fetching recipients for email ID: '{email_id}'...")
        
        query = """
            SELECT u.email FROM auth_user u
            JOIN mail_email_recipients er ON u.id = er.user_id
            WHERE er.email_id = ?
        """
        result = self._execute_query(query, (email_id,))
        recipients = [row['email'] for row in result]
        
        logger.info(f"[DB][SUCCESS] Retrieved {len(recipients)} recipient(s) for email ID: '{email_id}'.")
        return recipients