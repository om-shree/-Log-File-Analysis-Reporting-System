import re
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

class LogParser:
    LOG_PATTERN = re.compile(
        r'(\d+\.\d+\.\d+\.\d+) - - \[(.*?)\] "(.*?)" (\d{3}) (\d+) "(.*?)" "(.*?)"'
    )

    def parse_line(self, log_line):
        match = self.LOG_PATTERN.match(log_line)
        if match:
            try:
                ip, ts_str, request, status, bytes_sent, referrer, ua = match.groups()
                method, path, _ = request.split()
                timestamp = datetime.strptime(ts_str, '%d/%b/%Y:%H:%M:%S %z')
                return {
                    'ip_address': ip,
                    'timestamp': timestamp,
                    'method': method,
                    'path': path,
                    'status_code': int(status),
                    'bytes_sent': int(bytes_sent),
                    'referrer': referrer if referrer != "-" else None,
                    'user_agent': ua if ua != "-" else None
                }
            except Exception as e:
                logging.warning(f"Parse error: {e} | Line: {log_line.strip()}")
        return None
