import streamlit as st
import csv
import os
from datetime import datetime, date
from collections import defaultdict

EXPENSE_FILE = "expenses.csv"

DAILY_CATEGORIES = [
    "Food",
    "Car Petrol",
    "Movie Ticket",
    "New Clothes",
    "Haircut"
]

MONTHLY_CATEGORIES = [
    "Electricity",
    "Water",
    "Gym Membership",
    "OTT Subscription"
]

# -------------------- SESSION STATE INIT --------------------
if "expenses" not in st.session_state:
    st.session_state.expenses = []

    if os.path.exists(EXPENSE_FILE):
        with open(EXPENSE_FILE, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["Amount"] = float(row["Amount"])
                st.session_state.expenses.append(row)

# -------------------- FILE FUNCTIONS --------------------
def save_expenses():
    with open(EXPENSE_FILE, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["Date", "Expense_Type", "Category", "Amount", "Description"]
        )
        writer.writeheader()
        writer.writerows(st.session_state.expenses)


def add_expense(exp_date, exp_type, category, amount, desc):
    if amount <= 0:
        st.warning("Amount must be greater than 0")
        return

    st.session_state.expenses.append({
        "Date": exp_date.strftime("%Y-%m-%d"),
        "Expense_Type": exp_type,
        "Category": category,
        "Amount": amount,
        "Description": desc
    })
    save_expenses()


def remove_expense(index):
    st.session_state.expenses.pop(index)
    save_expenses()

# -------------------- DATA AGGREGATION --------------------
def generate_monthly_data():
    monthly = defaultdict(float)
    for exp in st.session_state.expenses:
        d = datetime.strptime(exp["Date"], "%Y-%m-%d")
        key = (d.year, d.month)
        monthly[key] += exp["Amount"]
    return monthly

# -------------------- CSV DOWNLOAD --------------------
def download_daily_csv():
    csv_data = "Date,Expense_Type,Category,Amount,Description\n"
    for e in st.session_state.expenses:
        csv_data += (
            f"{e['Date']},{e['Expense_Type']},"
            f"{e['Category']},{e['Amount']},{e['Description']}\n"
        )

    st.download_button(
        "Download Expenses CSV",
        csv_data,
        file_name="daily_expenses.csv",
        mime="text/csv"
    )

# -------------------- UI --------------------
st.set_page_config(page_title="Expense Tracker", layout="wide")
st.title("Srikar Expense Tracker")

# -------- Add Expense --------
st.header("Add Expense")

exp_type = st.radio(
    "Expense Type",
    ["Daily", "Monthly"],
    horizontal=True
)

exp_date = st.date_input("Date", value=date.today())

if exp_type == "Daily":
    category = st.selectbox("Category", DAILY_CATEGORIES)
else:
    category = st.selectbox("Category", MONTHLY_CATEGORIES)

amount = st.number_input("Amount", min_value=0.0, format="%.2f")
desc = st.text_input("Description")

if st.button("Add Expense"):
    add_expense(exp_date, exp_type, category, amount, desc)
    if amount > 0:
        st.success("Expense added successfully!")

# -------- View Expenses by Date --------
st.header("View Expenses by Date")

selected_date = st.date_input(
    "Select Date",
    value=date.today(),
    key="view_date"
)

selected_date_str = selected_date.strftime("%Y-%m-%d")

filtered_expenses = [
    e for e in st.session_state.expenses
    if e["Date"] == selected_date_str
]

if filtered_expenses:
    for i, exp in enumerate(filtered_expenses):
        col1, col2 = st.columns([6, 1])
        with col1:
            st.write(
                f"{exp['Date']} | {exp['Expense_Type']} | "
                f"{exp['Category']} | ₹{exp['Amount']} | {exp['Description']}"
            )
        with col2:
            original_index = st.session_state.expenses.index(exp)
            if st.button("Remove Expense", key=f"remove_{i}"):
                remove_expense(original_index)
                st.experimental_rerun()
else:
    st.info("No expenses recorded on this day.")

# -------- Downloads --------
st.header("Download Data")
download_daily_csv()
