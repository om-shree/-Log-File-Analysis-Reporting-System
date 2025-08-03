import argparse
from log_parser import LogParser
from mysql_handler import MySQLHandler
from configparser import ConfigParser
from tabulate import tabulate

def load_config():
    config = ConfigParser()
    config.read('config.ini')
    return {
        'host': config['mysql']['host'],
        'user': config['mysql']['user'],
        'password': config['mysql']['password'],
        'database': config['mysql']['database']
    }

def main():
    parser = argparse.ArgumentParser(description="Log File Analyzer CLI")
    subparsers = parser.add_subparsers(dest='command')

    process_parser = subparsers.add_parser("process_logs", help="Process and store logs in DB")
    process_parser.add_argument("file_path", help="Path to log file")

    report_parser = subparsers.add_parser("generate_report", help="Generate reports from DB")
    report_parser.add_argument("type", choices=["top_n_ips", "status_code_distribution", "hourly_traffic","top_n_pages", "traffic_by_os", "error_logs_by_date"])
    report_parser.add_argument("--n", type=int, default=5, help="Top N results")
    report_parser.add_argument("--date", type=str, help="Date for error logs (YYYY-MM-DD)")
    
    args = parser.parse_args()

    db = MySQLHandler(load_config())
    db.create_tables()

    if args.command == "process_logs":
        parser = LogParser()
        batch = []
        with open(args.file_path, encoding='utf-8') as f:
            for line in f:
                parsed = parser.parse_line(line)
                if parsed:
                    batch.append(parsed)
        db.insert_batch_log_entries(batch)
        print(f"Processed {len(batch)} entries.")
    elif args.command == "generate_report":
        if args.type == "top_n_ips":
            result = db.get_top_n_ips(args.n)
        elif args.type == "status_code_distribution":
            result = db.get_status_code_distribution()
        elif args.type == "hourly_traffic":
            result = db.get_hourly_traffic()
        elif args.type == "top_n_pages":
            result = db.get_top_n_pages(args.n)
        elif args.type == "traffic_by_os":
            result = db.get_traffic_by_os()
        elif args.type == "error_logs_by_date":
            if args.date:
                result = db.get_error_logs_by_date(args.date)
            else:
                print("Error: --date is required for error_logs_by_date")
                return
        else:
            result = []
        print(tabulate(result, headers="keys", tablefmt="grid"))

    db.close()

if __name__ == "__main__":
    main()
