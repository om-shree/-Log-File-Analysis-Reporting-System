# 📊 Log File Analysis & Reporting System

A command-line tool to parse, store, and analyze web server log files in Apache Common Log Format. This tool processes logs, stores them in a MySQL database, and generates insightful reports.

---

## 🚀 Features

- ✅ Parse Apache-style log files  
- ✅ Detect malformed lines  
- ✅ Normalize and store user agent data  
- ✅ Insert logs into MySQL with batch support  
- ✅ Generate analytical reports:
  - Top N IPs by request count  
  - HTTP status code distribution with percentage  
  - Hourly traffic trends
  - Top N most requested pages (URLs)
  - Traffic breakdown by Operating System
  - Error logs (4xx/5xx) filtered by date
- ✅ Pretty CLI output using `tabulate`

---

## 🛠 Requirements

- Python 3.9+
- MySQL Server
- Python packages:
  - `mysql-connector-python`
  - `tabulate`

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Create a `config.ini` file in the root directory:

```ini
[mysql]
host = localhost
user = your_mysql_user
password = your_mysql_password
database = log_analysis
```

---

## 🧪 Usage

### 🔹 Process Log File

```bash
python main.py process_logs /path/to/apache_log.log
```

Processes the given log file and stores parsed entries in the MySQL database.

### 🔹 Generate Reports

#### ▶ Top N IP Addresses

```bash
python main.py generate_report top_n_ips --n 10
```

#### ▶ Status Code Distribution

```bash
python main.py generate_report status_code_distribution
```

#### ▶ Hourly Traffic Report

```bash
python main.py generate_report hourly_traffic
```
#### ▶ Most requested pages
```bash
python main.py generate_report top_n_pages --n 10
```


#### ▶ Traffic by OS
```bash
python main.py generate_report traffic_by_os
```


#### ▶ Error logs for a date
```bash
python main.py generate_report error_logs_by_date --date 2025-07-30
```

---

## 🧱 Database Tables

- `log_entries`: stores parsed log records  
- `user_agents`: stores normalized OS, browser, and device type info

---

## 📂 Project Structure

```
log_analyzer_cli/
├── main.py
├── log_parser.py
├── mysql_handler.py
├── config.ini
├── requirements.txt
├── sample_logs/
└── sql/
```

---

## 💻 Full Command Summary

```bash
# Process logs
python main.py process_logs ./access.log

# Generate top N IPs
python main.py generate_report top_n_ips --n 10

# Generate status code distribution
python main.py generate_report status_code_distribution

# Generate hourly traffic report
python main.py generate_report hourly_traffic

# Most requested pages
python main.py generate_report top_n_pages --n 10

# Traffic by OS
python main.py generate_report traffic_by_os

# Error logs for a date
python main.py generate_report error_logs_by_date --date 2023-07-30
```

---

## 🙋‍♂️ Author

Omkar Navpute

---
