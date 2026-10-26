import streamlit as st
import pandas as pd

from db import (
    count_books,
    get_books,
    add_customer,
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
    ["Dashboard", "Register Customer", "Place Order"]
)

# Dashboard
if page == "Dashboard":
    try:
        total = count_books()
        st.metric("Total Books", total)

        books = get_books()

        df = pd.DataFrame(
            books,
            columns = [
                "Book ID", "Title", "Author", "Price", "Stock"
            ]
        )

        st.subheader("Book Catalogue")
        st.dataframe(df, use_container_width = True, hide_index = True)

    except Exception as e:
        st.error(f"Database error: {e}")


# Customer Registration
elif page == "Register Customer":
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
                customer_id = add_customer(
                    name.strip(), email.strip()
                )

                st.success("Customer registered successfully!")
                st.write("Your Customer ID:", customer_id)

            except Exception as e:
                st.error(f"Registration failed: {e}")

# Place Order
elif page == "Place Order":
    st.subheader("Place an Order")

    try:
        books = get_books()

        if not books:
            st.info("No books available.")
        else:
            book_options = {
                f"{b[1]} — ₹{b[3]} (Stock: {b[4]})": b
                for b in books
            }

            with st.form("order_form"):
                customer_id = st.number_input(
                    "Customer ID", min_value = 1, step = 1
                )

                selected = st.selectbox(
                    "Select Book", list(book_options.keys())
                )

                book = book_options[selected]

                quantity = st.number_input(
                    "Quantity",
                    min_value = 1,
                    max_value = max(1, int(book[4])),
                    step = 1
                )

                st.write(
                    f"Estimated Total: ₹{float(book[3]) * quantity:.2f}"
                )

                submitted = st.form_submit_button("Place Order")

            if submitted:
                if book[4] < quantity:
                    st.warning("Insufficient stock.")
                else:
                    place_order(
                        int(customer_id),
                        int(book[0]),
                        int(quantity)
                    )

                    st.success("Order placed successfully!")

    except Exception as e:
        st.error(f"Order failed: {e}")