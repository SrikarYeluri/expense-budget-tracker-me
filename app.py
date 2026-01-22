import streamlit as st
import csv
import os
from datetime import date

EXPENSE_FILE = "expenses.csv"

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
            fieldnames=["Date", "Category", "Type", "Amount", "Description"]
        )
        writer.writeheader()
        writer.writerows(st.session_state.expenses)


def add_expense(exp_date, category, expense_type, amount, desc):
    if amount <= 0:
        st.warning("Amount must be greater than 0")
        return

    st.session_state.expenses.append({
        "Date": exp_date.strftime("%Y-%m-%d"),
        "Category": category,
        "Type": expense_type,
        "Amount": amount,
        "Description": desc
    })
    save_expenses()


def remove_expense(index):
    st.session_state.expenses.pop(index)
    save_expenses()

# -------------------- UI --------------------
st.set_page_config(page_title="Expense Tracker", layout="wide")
st.title("Srikar Expense Tracker")

# -------- Add Expense --------
st.header("Add Daily Expense")

exp_date = st.date_input("Date", value=date.today())

category = st.selectbox(
    "Category",
    [
        "Food",
        "Transport",
        "Entertainment",
        "Shopping",
        "Personal Care",
        "Utilities",
        "Fitness",
        "Subscriptions"
    ]
)

expense_type_map = {
    "Food": ["Breakfast", "Lunch", "Dinner"],
    "Transport": ["Car Petrol", "Cab"],
    "Entertainment": ["Movie Ticket", "Games"],
    "Shopping": ["New Clothes", "Accessories"],
    "Personal Care": ["Haircut"],
    "Utilities": ["Electricity", "Water","Rent"],
    "Fitness": ["Gym Membership"],
    "Subscriptions": ["OTT Subscription"]
}

expense_type = st.selectbox(
    "Expense Type",
    expense_type_map.get(category, [])
)

amount = st.number_input("Amount (Rs)", min_value=0.0, format="%.2f")
desc = st.text_input("Description (Optional)")

if st.button("Add Expense"):
    add_expense(exp_date, category, expense_type, amount, desc)
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
                f"{exp['Date']} | {exp['Category']} | {exp['Type']} | Rs{exp['Amount']} | {exp['Description']}"
            )
        with col2:
            original_index = st.session_state.expenses.index(exp)
            if st.button("Remove", key=f"remove_{i}"):
                remove_expense(original_index)
                st.experimental_rerun()
else:
    st.info("No expenses recorded on this day.")

# -------- Download Daily CSV --------
st.header("Download Daily Expenses")

csv_data = "Date,Category,Type,Amount,Description\n"
for e in st.session_state.expenses:
    csv_data += f"{e['Date']},{e['Category']},{e['Type']},{e['Amount']},{e['Description']}\n"

st.download_button(
    "Download Daily Expenses CSV",
    csv_data,
    file_name="daily_expenses.csv",
    mime="text/csv"
)
