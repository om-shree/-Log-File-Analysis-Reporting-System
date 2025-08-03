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
    report_parser.add_argument("type", choices=["top_n_ips", "status_code_distribution", "hourly_traffic"])
    report_parser.add_argument("--n", type=int, default=5, help="Top N IPs (for top_n_ips report)")

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
        else:
            result = []
        print(tabulate(result, headers="keys", tablefmt="grid"))

    db.close()

if __name__ == "__main__":
    main()
