import streamlit as st
import csv
import os
from datetime import datetime, date
from collections import defaultdict

EXPENSE_FILE = "expenses.csv"
BUDGET_FILE = "budget.csv"

# -------------------- SESSION STATE INIT --------------------
if "expenses" not in st.session_state:
    st.session_state.expenses = []

    if os.path.exists(EXPENSE_FILE):
        with open(EXPENSE_FILE, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["Amount"] = float(row["Amount"])
                st.session_state.expenses.append(row)

# -------------------- BUDGET FUNCTIONS --------------------
def save_budget(month, year, budget):
    with open(BUDGET_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Month", "Year", "Budget"])
        writer.writerow([month, year, budget])


def load_budget():
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                return row
    return None

# -------------------- EXPENSE FUNCTIONS --------------------
def save_expenses():
    with open(EXPENSE_FILE, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["Date", "Category", "Amount", "Description"]
        )
        writer.writeheader()
        writer.writerows(st.session_state.expenses)


def add_expense(exp_date, category, amount, desc):
    if amount <= 0:
        st.warning("Amount must be greater than 0")
        return

    st.session_state.expenses.append({
        "Date": exp_date.strftime("%Y-%m-%d"),
        "Category": category,
        "Amount": amount,
        "Description": desc
    })
    save_expenses()

# -------------------- DATA AGGREGATION --------------------
def generate_weekly_data():
    weekly = defaultdict(float)
    for exp in st.session_state.expenses:
        d = datetime.strptime(exp["Date"], "%Y-%m-%d")
        week_key = f"{d.year}-W{d.isocalendar()[1]}"
        weekly[week_key] += exp["Amount"]
    return weekly


def generate_monthly_data():
    monthly = defaultdict(float)
    for exp in st.session_state.expenses:
        d = datetime.strptime(exp["Date"], "%Y-%m-%d")
        month_key = d.strftime("%Y-%m")
        monthly[month_key] += exp["Amount"]
    return monthly


def download_csv(filename, header, rows):
    csv_data = ",".join(header) + "\n"
    for row in rows:
        csv_data += ",".join(map(str, row)) + "\n"
    st.download_button(
        label=f"Download {filename}",
        data=csv_data,
        file_name=filename,
        mime="text/csv"
    )

# -------------------- UI --------------------
st.title("Personal Expense & Budget Tracker")

# -------- Budget Section --------
st.header("Set Monthly Budget")

budget_month = st.selectbox("Month", list(range(1, 13)))
budget_year = st.number_input("Year", value=date.today().year, step=1)
budget_amount = st.number_input("Monthly Budget", min_value=0.0)

if st.button("Save Budget"):
    save_budget(budget_month, budget_year, budget_amount)
    st.success("Budget saved successfully!")

saved_budget = load_budget()
if saved_budget:
    st.info(
        f"Current Budget: ₹{saved_budget['Budget']} "
        f"for {saved_budget['Month']}/{saved_budget['Year']}"
    )

# -------- Expense Entry --------
st.header("Add Daily Expense")

exp_date = st.date_input("Date", value=date.today())
category = st.selectbox(
    "Category",
    ["Food", "Transport", "Entertainment", "Utilities", "Other"]
)
amount = st.number_input("Amount", min_value=0.0, format="%.2f")
desc = st.text_input("Description")

if st.button("Add Expense"):
    add_expense(exp_date, category, amount, desc)
    if amount > 0:
        st.success("Expense added!")

# -------- Expense Table --------
st.header("All Expenses")

if st.session_state.expenses:
    st.table(st.session_state.expenses)
else:
    st.write("No expenses recorded yet.")

# -------- Download Section --------
st.header("Download Data for Excel")

# Daily
download_csv(
    "daily_expenses.csv",
    ["Date", "Category", "Amount", "Description"],
    [[e["Date"], e["Category"], e["Amount"], e["Description"]]
     for e in st.session_state.expenses]
)

# Weekly
weekly_data = generate_weekly_data()
download_csv(
    "weekly_expenses.csv",
    ["Week", "Total Amount"],
    weekly_data.items()
)

# Monthly
monthly_data = generate_monthly_data()
download_csv(
    "monthly_expenses.csv",
    ["Month", "Total Amount"],
    monthly_data.items()
)

