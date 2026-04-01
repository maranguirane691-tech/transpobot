import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    url = os.getenv("MYSQL_PUBLIC_URL")
    if url:
        # Connexion via URL Railway
        import re
        match = re.match(r'mysql://(\w+):(.+)@(.+):(\d+)/(\w+)', url)
        if match:
            user, password, host, port, database = match.groups()
            return mysql.connector.connect(
                host=host,
                port=int(port),
                user=user,
                password=password,
                database=database
            )
    # Connexion locale
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "transpobot")
    )