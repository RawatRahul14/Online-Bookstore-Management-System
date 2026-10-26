import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")
ORACLE_DSN = os.getenv("ORACLE_DSN")

try:

    connection = oracledb.connect(
        user = ORACLE_USER,
        password = ORACLE_PASSWORD,
        dsn = ORACLE_DSN
    )

    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            SYS_CONTEXT('USERENV', 'SESSION_USER'),
            SYS_CONTEXT('USERENV', 'SERVICE_NAME')
        FROM dual
    """)

    print("Connection successful!")
    print("Database details:", cursor.fetchone())

    cursor.close()
    connection.close()

except Exception as e:
    print("Connection failed!")
    print(e)