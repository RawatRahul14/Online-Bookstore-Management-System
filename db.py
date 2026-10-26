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

# --- Functions ---

def count_books():
    with connect() as conn:
        with conn.cursor() as cur:
            return cur.callfunc("count_books", int)

def get_book_price(book_id):
    with connect() as conn:
        with conn.cursor() as cur:
            return cur.callfunc(
                "get_book_price",
                float,
                [book_id]
            )

def get_total_revenue():
    with connect() as conn:
        with conn.cursor() as cur:
            return cur.callfunc("get_total_revenue", float)

def get_customer_spending(customer_id):
    with connect() as conn:
        with conn.cursor() as cur:
            return cur.callfunc(
                "get_customer_spending",
                float,
                [customer_id]
            )

# --- Queries ---

def get_books():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT book_id, title, author, price, stock "
                "FROM books ORDER BY book_id"
            )
            return cur.fetchall()

def get_customers():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT customer_id, name, email "
                "FROM customers ORDER BY customer_id"
            )
            return cur.fetchall()

def get_orders():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT o.order_id, c.name, b.title, o.quantity, o.total, o.order_date
                FROM orders o
                JOIN customers c ON o.customer_id = c.customer_id
                JOIN books b ON o.book_id = b.book_id
                ORDER BY o.order_date DESC, o.order_id DESC
                """
            )
            return cur.fetchall()

# --- Procedures ---

def add_customer(name, email):
    with connect() as conn:
        with conn.cursor() as cur:
            customer_id = cur.var(int)
            cur.callproc(
                "register_customer",
                [name, email, customer_id]
            )
            conn.commit()

            new_id = customer_id.getvalue()
            if isinstance(new_id, list):
                new_id = new_id[0]
            return int(new_id)

def add_book(title, author, price, stock):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.callproc(
                "add_book",
                [title, author, price, stock]
            )
        conn.commit()

def restock_book(book_id, quantity):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.callproc(
                "restock_book",
                [book_id, quantity]
            )
        conn.commit()

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