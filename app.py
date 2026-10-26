import streamlit as st
import pandas as pd

from db import (
    count_books,
    get_total_revenue,
    get_customer_spending,
    get_books,
    get_customers,
    get_orders,
    add_customer,
    add_book,
    restock_book,
    place_order
)

st.set_page_config(
    page_title = "Online Bookstore",
    page_icon = "📚",
    layout = "wide"
)

st.title("📚 Online Bookstore")
st.caption("Python + Streamlit + Oracle PL/SQL")

page = st.sidebar.selectbox(
    "Select Page",
    ["Dashboard", "Manage Inventory", "Customers", "Place Order"]
)

# 1. Dashboard
if page == "Dashboard":
    try:
        total_books = count_books()
        revenue = get_total_revenue()
        orders = get_orders()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Books", total_books)
        col2.metric("Total Orders", len(orders))
        col3.metric("Total Revenue", f"₹{revenue:,.2f}")

        tab1, tab2 = st.tabs(["📖 Book Catalogue", "🧾 Order History"])

        with tab1:
            books = get_books()
            df_books = pd.DataFrame(
                books,
                columns = ["Book ID", "Title", "Author", "Price (₹)", "Stock"]
            )
            st.dataframe(df_books, use_container_width = True, hide_index = True)

        with tab2:
            if not orders:
                st.info("No orders have been placed yet.")
            else:
                df_orders = pd.DataFrame(
                    orders,
                    columns = ["Order ID", "Customer", "Book", "Qty", "Total (₹)", "Date"]
                )
                st.dataframe(df_orders, use_container_width = True, hide_index = True)

    except Exception as e:
        st.error(f"Database error: {e}")

# 2. Manage Inventory
elif page == "Manage Inventory":
    tab1, tab2 = st.tabs(["+ Add New Book", "📦 Restock Book"])

    with tab1:
        st.subheader("Add a New Book")
        with st.form("add_book_form"):
            title = st.text_input("Book Title")
            author = st.text_input("Author")
            price = st.number_input("Price (₹)", min_value = 1.0, value = 499.0, step = 10.0)
            stock = st.number_input("Initial Stock", min_value = 0, value = 10, step = 1)
            submitted = st.form_submit_button("Add Book")

        if submitted:
            if not title.strip() or not author.strip():
                st.warning("Please enter both title and author.")
            else:
                try:
                    add_book(title.strip(), author.strip(), float(price), int(stock))
                    st.success(f"Added '{title}' to catalogue!")
                except Exception as e:
                    st.error(f"Failed to add book: {e}")

    with tab2:
        st.subheader("Restock Existing Book")
        try:
            books = get_books()
        except Exception as e:
            st.error(f"Could not load books: {e}")
            books = []

        if not books:
            st.info("No books available to restock.")
        else:
            book_map = {f"{b[1]} (Current Stock: {b[4]})": b[0] for b in books}
            with st.form("restock_form"):
                selected_label = st.selectbox("Select Book", list(book_map.keys()))
                qty = st.number_input("Quantity to Add", min_value = 1, value = 5, step = 1)
                restock_btn = st.form_submit_button("Update Stock")

            if restock_btn:
                try:
                    restock_book(int(book_map[selected_label]), int(qty))
                    st.success("Stock updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error restocking book: {e}")

# 3. Customers
elif page == "Customers":
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Register a Customer")
        with st.form("customer_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            submitted = st.form_submit_button("Register")

        if submitted:
            if not name.strip() or "@" not in email:
                st.warning("Enter a name and a valid email address.")
            else:
                try:
                    customer_id = add_customer(name.strip(), email.strip())
                    st.success(f"Customer registered! Assigned ID: {customer_id}")
                except Exception as e:
                    st.error(f"Registration failed: {e}")

    with col2:
        st.subheader("Customer Spending Lookup")
        try:
            customers = get_customers()
            if not customers:
                st.info("No registered customers yet.")
            else:
                cust_map = {f"{c[1]} ({c[2]})": c[0] for c in customers}
                selected_cust = st.selectbox("Select Customer", list(cust_map.keys()))
                spent = get_customer_spending(int(cust_map[selected_cust]))
                st.metric("Total Spent by Customer", f"₹{spent:,.2f}")
        except Exception as e:
            st.error(f"Could not load customers: {e}")

# 4. Place Order
elif page == "Place Order":
    st.subheader("Place an Order")

    try:
        books = get_books()
        customers = get_customers()
    except Exception as e:
        st.error(f"Could not load order form data: {e}")
        books = []
        customers = []

    if not books:
        st.info("No books available in the store.")
    elif not customers:
        st.info("Please register a customer before placing an order.")
    else:
        cust_options = {f"{c[1]} (ID: {c[0]})": c[0] for c in customers}
        book_options = {
            f"{b[1]} — ₹{b[3]} (Stock: {b[4]})": b
            for b in books
        }

        selected_cust_label = st.selectbox("Customer", list(cust_options.keys()))
        selected_book_label = st.selectbox("Select Book", list(book_options.keys()))
        book = book_options[selected_book_label]

        if int(book[4]) == 0:
            st.warning("This book is currently out of stock.")
        else:
            quantity = st.number_input(
                "Quantity",
                min_value = 1,
                max_value = int(book[4]),
                step = 1
            )

            st.info(f"**Estimated Total:** ₹{float(book[3]) * quantity:,.2f}")

            if st.button("Place Order", type = "primary"):
                try:
                    place_order(
                        int(cust_options[selected_cust_label]),
                        int(book[0]),
                        int(quantity)
                    )
                    st.success("Order placed successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Order failed: {e}")