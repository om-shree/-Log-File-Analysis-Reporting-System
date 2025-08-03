
import mysql.connector

def connect_db(config):
    return mysql.connector.connect(
        host=config.get("mysql", "host"),
        user=config.get("mysql", "user"),
        password=config.get("mysql", "password"),
        database=config.get("mysql", "database")
    )

def top_ips(conn, limit=10):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ip_address, COUNT(*) as count
        FROM logs
        GROUP BY ip_address
        ORDER BY count DESC
        LIMIT %s
    """, (limit,))
    return cursor.fetchall()

def top_paths(conn, limit=10):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT path, COUNT(*) as count
        FROM logs
        GROUP BY path
        ORDER BY count DESC
        LIMIT %s
    """, (limit,))
    return cursor.fetchall()

def status_code_summary(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT status_code, COUNT(*) as count
        FROM logs
        GROUP BY status_code
        ORDER BY status_code
    """)
    return cursor.fetchall()

def traffic_by_hour(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT HOUR(timestamp) as hour, COUNT(*) as count
        FROM logs
        GROUP BY hour
        ORDER BY hour
    """)
    return cursor.fetchall()

def user_agent_summary(conn, limit=5):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_agent, COUNT(*) as count
        FROM logs
        WHERE user_agent IS NOT NULL
        GROUP BY user_agent
        ORDER BY count DESC
        LIMIT %s
    """, (limit,))
    return cursor.fetchall()
