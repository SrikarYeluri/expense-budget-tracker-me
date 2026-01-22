import streamlit as st
import csv
import os
from datetime import datetime

FILE_PATH = "expenses.csv"

# -------------------- SESSION STATE INIT --------------------
if "expenses" not in st.session_state:
    st.session_state.expenses = []

    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["Amount"] = float(row["Amount"])  # FIX: ensure float
                st.session_state.expenses.append(row)

# -------------------- DATA FUNCTIONS --------------------
def add_expense(date, category, amount, description):
    # FIX 2: validation
    if amount <= 0:
        st.warning("Amount must be greater than 0")
        return

    new_expense = {
        # FIX 1: consistent date format
        "Date": date.strftime("%Y-%m-%d"),
        "Category": category,
        "Amount": float(amount),
        "Description": description
    }

    st.session_state.expenses.append(new_expense)
    save_expenses()


def save_expenses():
    with open(FILE_PATH, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["Date", "Category", "Amount", "Description"]
        )
        writer.writeheader()
        for exp in st.session_state.expenses:
            writer.writerow(exp)


def load_expenses():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", newline="") as f:
            reader = csv.DictReader(f)
            data = []
            for row in reader:
                row["Amount"] = float(row["Amount"])  # FIX: float conversion
                data.append(row)
            st.session_state.expenses = data
        st.success("Expenses loaded successfully!")
    else:
        st.warning("No saved expenses found!")

# -------------------- VISUALIZATION --------------------
def daily_trend(selected_category):
    if not st.session_state.expenses:
        st.warning("No expenses to show!")
        return

    daily_totals = {}

    for exp in st.session_state.expenses:
        if selected_category != "All" and exp["Category"] != selected_category:
            continue

        date = exp["Date"]
        amount = exp["Amount"]
        daily_totals[date] = daily_totals.get(date, 0) + amount

    if daily_totals:
        sorted_dates = sorted(daily_totals.keys())
        sorted_values = [daily_totals[d] for d in sorted_dates]
        st.line_chart({"Amount": sorted_values}, x=sorted_dates)
    else:
        st.info("No data for this category.")


def monthly_comparison(selected_category):
    if not st.session_state.expenses:
        st.warning("No expenses to show!")
        return

    monthly_totals = {}

    for exp in st.session_state.expenses:
        if selected_category != "All" and exp["Category"] != selected_category:
            continue

        try:
            dt = datetime.strptime(exp["Date"], "%Y-%m-%d")
        except ValueError:
            continue

        month_key = dt.strftime("%Y-%m")
        monthly_totals[month_key] = monthly_totals.get(month_key, 0) + exp["Amount"]

    if monthly_totals:
        sorted_months = sorted(monthly_totals.keys())
        sorted_values = [monthly_totals[m] for m in sorted_months]
        st.bar_chart({"Amount": sorted_values}, x=sorted_months)
    else:
        st.info("No data for this category.")


def category_breakdown():
    if not st.session_state.expenses:
        st.warning("No expenses to show!")
        return

    category_totals = {}

    for exp in st.session_state.expenses:
        category = exp["Category"]
        amount = exp["Amount"]
        category_totals[category] = category_totals.get(category, 0) + amount

    st.bar_chart(
        {"Amount": list(category_totals.values())},
        x=list(category_totals.keys())
    )

# -------------------- UI --------------------
st.title("DevDuniya Expense Tracker")

with st.sidebar:
    st.header("Add Expense")

    date = st.date_input("Date")
    category = st.selectbox(
        "Category",
        ["Food", "Transport", "Entertainment", "Utilities", "Other"]
    )
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    description = st.text_input("Description")

    if st.button("Add"):
        add_expense(date, category, amount, description)
        if amount > 0:
            st.success("Expense added!")

    st.header("File Operations")
    if st.button("Save Expenses"):
        save_expenses()
        st.success("Expenses saved!")

    if st.button("Load Expenses"):
        load_expenses()

# -------------------- FILTER --------------------
st.header("Filter")
selected_category = st.selectbox(
    "Select Category for Trend/Comparison",
    ["All", "Food", "Transport", "Entertainment", "Utilities", "Other"]
)

# -------------------- TABLE --------------------
st.header("Expenses Table")

if st.session_state.expenses:
    if selected_category == "All":
        st.table(st.session_state.expenses)
    else:
        filtered = [
            exp for exp in st.session_state.expenses
            if exp["Category"] == selected_category
        ]
        st.table(filtered)
else:
    st.write("No expenses yet.")

# -------------------- CHARTS --------------------
st.header("Daily Trend")
daily_trend(selected_category)

st.header("Monthly Comparison")
monthly_comparison(selected_category)

st.header("Category Breakdown (All Categories)")
category_breakdown()








