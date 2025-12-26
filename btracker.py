import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(
    page_title="Budget Tracker",
    layout="centered"
)

DATA_FILE = "data.csv"

CATEGORIES = [
    "Food",
    "Transport",
    "Rent",
    "Utilities",
    "Internet",
    "Phone",
    "Entertainment",
    "Shopping",
    "Health",
    "Education",
    "Subscriptions",
    "Travel",
    "Gifts",
    "Salary",
    "Savings",
    "Other"
]

# ---------------- DATA FUNCTIONS ----------------
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["date", "type", "category", "amount", "note"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)


# ---------------- LOAD DATA ----------------
df = load_data()

if not df.empty:
    df["date"] = pd.to_datetime(df["date"], errors = "coerce")
    df = df.dropna(subset=["date"])

    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        st.error("Date column is not in datetime format.")
        st.stop()



# ---------------- UI ----------------
st.title("Budget Tracker")


# -------- ADD TRANSACTION --------
st.subheader("Add Transaction")

with st.form("transaction form", clear_on_submit=True):
    trans_type = st.selectbox("Type", ["Income", "Expense"])
    trans_date = st.date_input("Date", date.today())
    category = st.selectbox("Category", CATEGORIES)
    amount = st.number_input("Amount", min_value=0, format="%.2f")
    note = st.text_input("Note (optional)")
    submit = st.form_submit_button("Add")
    if submit:
        new_row = pd.DataFrame([{
            "date": pd.to_datetime(trans_date),
            "type": trans_type,
            "category": category,
            "amount": amount,
            "note": note
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        save_data(df)
        st.success("Transaction saved!")
    

# -------- FILTERS --------

st.subheader("Filters")

if df.empty:
    st.info("No data yet.")
    st.stop()
df["month"] = df['date'].dt.strftime("%Y-%m")

month_filter = st.selectbox(
    "Month",
    ["All"] + sorted(df["month"].unique().tolist())
)

category_filter = st.selectbox(
    "Category",
    ["All"] + CATEGORIES
)

filtered_df = df.copy()

if month_filter != "All":
    filtered_df = filtered_df[filtered_df["month"] == month_filter]

if category_filter != "All":
    filtered_df = filtered_df[filtered_df["category"] == category_filter]


# -------- SUMMARY --------

st.subheader("Summary")

income = filtered_df[filtered_df["type"] == "Income"]["amount"].sum()
expense = filtered_df[filtered_df["type"] == "Expense"]["amount"].sum()
balance = income - expense

col1, col2, col3 = st.columns(3)
col1.metric("Income", f"${income: .2f}")
col2.metric("Expenses", f"${expense: .2f}")
col3.metric("Balance", f"${balance: .2f}")


# -------- CHARTS (FAST) --------
st.subheader("Expense by Category")

# Create a separate DataFrame for chart that only filters by month

chart_df = df.copy()
if month_filter != "All":
    chart_df = chart_df[chart_df["month"] == month_filter]
expenses = chart_df[chart_df["type"] == "Expense"]

if not expenses.empty:
    cat_sum = expenses.groupby("category")["amount"].sum()
    st.bar_chart(cat_sum)
else:
    st.info("No expenses to display.")
st.subheader("Monthly Totals")

monthly_sum = (
    df.groupby("month")["amount"]
    .sum()
    .sort_index()
)
st.line_chart(monthly_sum)
