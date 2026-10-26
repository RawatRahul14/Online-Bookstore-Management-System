import os
import oracledb
from dotenv import load_dotenv

load_dotenv()

def connect():
    return oracledb.connect(
        user = os.getenv("ORACLE_USER"),
        password = os.getenv("ORACLE_PASSWORD"),
        dsn = os.getenv("ORACLE_DSN")
    )

def count_books():
    with connect() as conn:
        with conn.cursor() as cur:
            return cur.callfunc("count_books", int)

def get_book_price(book_id):
    with connect() as conn:
        with conn.cursor() as cur:
            return cur.callfunc(
                "get_book_price",
                oracledb.DB_TYPE_NUMBER,
                [book_id]
            )

def get_books():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT book_id, title, author, price, stock "
                "FROM books ORDER BY book_id"
            )
            return cur.fetchall()

def add_customer(name, email):
    with connect() as conn:
        with conn.cursor() as cur:
            customer_id = cur.var(int)

            cur.execute(
                """
                INSERT INTO customers (name, email)
                VALUES (:name, :email)
                RETURNING customer_id INTO :customer_id
                """,
                name = name,
                email =email,
                customer_id = customer_id
            )

            new_id = customer_id.getvalue()
            conn.commit()

            if isinstance(new_id, list):
                new_id = new_id[0]

            return int(new_id)

def place_order(customer_id, book_id, quantity):
    with connect() as conn:
        try:
            with conn.cursor() as cur:
                cur.callproc(
                    "place_order",
                    [customer_id, book_id, quantity]
                )

            conn.commit()

        except Exception:
            conn.rollback()
            raise