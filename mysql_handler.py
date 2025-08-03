import mysql.connector
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)

class MySQLHandler:
    def __init__(self, config):
        # Allow optional 'port' in config.ini
        if 'port' in config and isinstance(config['port'], str):
            try:
                config['port'] = int(config['port'])
            except ValueError:
                pass
        self.conn = mysql.connector.connect(**config)
        # dictionary=True so we can get dict rows for tabulate
        self.cursor = self.conn.cursor(dictionary=True)

    def create_tables(self):
        with open('sql/create_tables.sql', encoding='utf-8') as f:
            sql = f.read()
        # Execute statements separated by ;
        for stmt in sql.split(';'):
            if stmt.strip():
                self.cursor.execute(stmt)
        self.conn.commit()

    # --- Internal helpers ---

    def _normalize_ts(self, dt: datetime) -> datetime:
        """
        Convert timezone-aware dat6etime to naive UTC for MySQL DATETIME.
        MySQL DATETIME has no timezone; we store UTC without tzinfo.
        """
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt

    def _get_or_insert_user_agent(self, ua: str | None):
        if not ua:
            return None

        self.cursor.execute(
            "SELECT id FROM user_agents WHERE user_agent_string = %s",
            (ua,)
        )
        row = self.cursor.fetchone()
        if row:
            return row['id']

        # very lightweight UA parsing (keep it simple; avoids extra deps)
        os_name = "Unknown OS"
        browser = "Unknown Browser"
        device = "Desktop"

        ua_lc = ua.lower()
        if "windows" in ua_lc:
            os_name = "Windows"
        elif "mac os" in ua_lc or "macintosh" in ua_lc:
            os_name = "macOS"
        elif "linux" in ua_lc:
            os_name = "Linux"
        elif "android" in ua_lc:
            os_name = "Android"
        elif "iphone" in ua_lc or "ios" in ua_lc:
            os_name = "iOS"

        if "chrome" in ua_lc and "safari" in ua_lc:
            browser = "Chrome"
        elif "firefox" in ua_lc:
            browser = "Firefox"
        elif "safari" in ua_lc and "chrome" not in ua_lc:
            browser = "Safari"
        elif "edge" in ua_lc:
            browser = "Edge"

        if "mobile" in ua_lc:
            device = "Mobile"
        elif "tablet" in ua_lc or "ipad" in ua_lc:
            device = "Tablet"

        self.cursor.execute(
            """
            INSERT INTO user_agents (user_agent_string, os, browser, device_type)
            VALUES (%s, %s, %s, %s)
            """,
            (ua, os_name, browser, device)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    # --- Inserts ---

    def insert_batch_log_entries(self, log_data_list: list[dict]):
        """
        Insert parsed log entries. Expects dicts with:
        ip_address,timestamp,method,path,status_code,bytes_sent,referrer,user_agent
        """
        if not log_data_list:
            return

        insert_sql = """
        INSERT IGNORE INTO log_entries
            (ip_address, timestamp, method, path, status_code, bytes_sent, referrer, user_agent_id)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s)
        """


        for data in log_data_list:
            user_agent_id = self._get_or_insert_user_agent(data.get('user_agent'))
            ts = self._normalize_ts(data['timestamp'])

            params = (
                data['ip_address'],
                ts,
                data['method'],
                data['path'],
                int(data['status_code']),
                int(data['bytes_sent']),
                data.get('referrer'),
                user_agent_id
            )
            self.cursor.execute(insert_sql, params)

        self.conn.commit()

    # --- Reports ---

    def get_top_n_ips(self, n: int):
        self.cursor.execute(
            """
            SELECT ip_address, COUNT(*) AS request_count
            FROM log_entries
            GROUP BY ip_address
            ORDER BY request_count DESC
            LIMIT %s
            """,
            (n,)
        )
        return self.cursor.fetchall()

    def get_status_code_distribution(self):
        self.cursor.execute(
            """
            SELECT
              status_code,
              COUNT(*) AS count,
              (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM log_entries)) AS percentage
            FROM log_entries
            GROUP BY status_code
            ORDER BY count DESC
            """
        )
        return self.cursor.fetchall()

    def get_hourly_traffic(self):
        # Use HOUR() + LPAD to avoid DATE_FORMAT quirks across environments
        self.cursor.execute(
            """
            SELECT CONCAT(LPAD(HOUR(`timestamp`), 2, '0'), ':00') AS hour_of_day,
                COUNT(*) AS request_count
            FROM log_entries
            GROUP BY hour_of_day
            ORDER BY hour_of_day ASC
            """
        )
        return self.cursor.fetchall()


    def close(self):
        self.cursor.close()
        self.conn.close()
