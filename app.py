import streamlit as st
import pytesseract
from PIL import Image
import re
import pandas as pd

# -----------------------------
# Page configuration
# -----------------------------

st.set_page_config(
    page_title="AI Financial Advisor - Week 1",
    page_icon="💰",
    layout="wide"
)

st.title("💰 AI Financial Advisor & Expense Manager")
st.caption("Week 1 Basic Prototype — OCR + Expense Extraction + Basic Financial Advice")


# -----------------------------
# Helper functions
# -----------------------------

def extract_amount(text):

    patterns = [
        r'(?:₹|Rs\.?|INR)\s*([0-9,]+(?:\.[0-9]{1,2})?)',
        r'(?:amount|paid|total|debit|spent)\s*[:\-]?\s*(?:₹|Rs\.?|INR)?\s*([0-9,]+(?:\.[0-9]{1,2})?)'
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)

        if matches:
            try:
                return float(matches[-1].replace(",", ""))
            except ValueError:
                pass

    return None


def extract_date(text):

    patterns = [
        r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
        r'\b(\d{2,4}[/-]\d{1,2}[/-]\d{1,2})\b'
    ]

    for pattern in patterns:
        m = re.search(pattern, text)

        if m:
            return m.group(1)

    return "Not detected"


def extract_merchant(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    keywords = [
        "swiggy",
        "zomato",
        "uber",
        "ola",
        "amazon",
        "flipkart",
        "dmart",
        "blinkit",
        "zepto",
        "netflix",
        "google pay",
        "phonepe",
        "paytm"
    ]

    lower_text = text.lower()

    for keyword in keywords:

        if keyword in lower_text:
            return keyword.title()

    # Fallback
    for line in lines:

        if len(line) > 2 and not re.search(r'\d{2,}', line):
            return line[:40]

    return "Unknown"


def categorize(merchant, text):

    combined = f"{merchant} {text}".lower()

    category_keywords = {

        "Food": [
            "swiggy",
            "zomato",
            "restaurant",
            "food",
            "domino",
            "pizza"
        ],

        "Transport": [
            "uber",
            "ola",
            "rapido",
            "metro",
            "bus",
            "petrol",
            "fuel"
        ],

        "Shopping": [
            "amazon",
            "flipkart",
            "myntra",
            "shopping"
        ],

        "Groceries": [
            "dmart",
            "blinkit",
            "zepto",
            "grocery",
            "groceries"
        ],

        "Entertainment": [
            "netflix",
            "spotify",
            "movie",
            "cinema"
        ],

        "Bills": [
            "electricity",
            "recharge",
            "internet",
            "mobile",
            "bill"
        ],

        "Healthcare": [
            "hospital",
            "pharmacy",
            "medical",
            "medicine"
        ],

        "Education": [
            "college",
            "course",
            "book",
            "education"
        ]
    }

    for category, words in category_keywords.items():

        if any(word in combined for word in words):
            return category

    return "Others"


def generate_advice(amount, category):

    if amount is None:
        return (
            "I could not detect the transaction amount. "
            "Please enter or correct it manually."
        )

    advice = (
        f"The detected transaction is ₹{amount:,.2f} "
        f"under {category}."
    )

    if category in ["Food", "Shopping", "Entertainment"]:

        advice += (
            " Track discretionary spending in this category "
            "and consider setting a monthly budget."
        )

    elif category in ["Bills", "Transport", "Groceries"]:

        advice += (
            " Monitor recurring expenses and compare them "
            "with your monthly budget."
        )

    else:

        advice += (
            " Continue tracking this expense so your monthly "
            "spending pattern can be analyzed."
        )

    return advice


# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.header("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Upload Expense",
        "Basic Dashboard",
        "AI Advice"
    ]
)


# -----------------------------
# Session state
# -----------------------------

if "transactions" not in st.session_state:
    st.session_state.transactions = []


# -----------------------------
# Upload Expense
# -----------------------------

if page == "Upload Expense":

    st.header("1️⃣ Upload Payment Screenshot")

    uploaded = st.file_uploader(
        "Upload a payment screenshot",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded:

        image = Image.open(uploaded)

        st.image(
            image,
            caption="Uploaded payment screenshot",
            width=450
        )

        if st.button("🔍 Extract Expense"):

            with st.spinner("Running OCR..."):

                try:

                    text = pytesseract.image_to_string(image)

                except Exception:

                    text = ""

                    st.error(
                        "OCR could not run. "
                        "Make sure Tesseract OCR is installed "
                        "and configured."
                    )

            st.subheader("OCR Text")

            if text.strip():

                st.code(text)

            else:

                st.warning(
                    "No text detected. "
                    "Try a clearer screenshot."
                )

            # Extract information

            amount = extract_amount(text)
            date = extract_date(text)
            merchant = extract_merchant(text)
            category = categorize(merchant, text)

            st.subheader("Extracted Transaction")

            c1, c2 = st.columns(2)

            with c1:

                merchant_edit = st.text_input(
                    "Merchant",
                    merchant
                )

                amount_edit = st.number_input(
                    "Amount (₹)",
                    min_value=0.0,
                    value=float(amount or 0.0),
                    step=10.0
                )

            with c2:

                date_edit = st.text_input(
                    "Date",
                    date
                )

                categories = [
                    "Food",
                    "Transport",
                    "Shopping",
                    "Groceries",
                    "Entertainment",
                    "Bills",
                    "Healthcare",
                    "Education",
                    "Others"
                ]

                category_edit = st.selectbox(
                    "Category",
                    categories,
                    index=categories.index(category)
                )

            if st.button("✅ Confirm & Save Transaction"):

                st.session_state.transactions.append({

                    "Date": date_edit,

                    "Merchant": merchant_edit,

                    "Amount": amount_edit,

                    "Category": category_edit,

                    "Source": "Screenshot"
                })

                st.success(
                    "Transaction saved successfully!"
                )

                st.info(
                    generate_advice(
                        amount_edit,
                        category_edit
                    )
                )


# -----------------------------
# Dashboard
# -----------------------------

elif page == "Basic Dashboard":

    st.header("2️⃣ Basic Expense Dashboard")

    if not st.session_state.transactions:

        st.info(
            "No transactions yet. "
            "Upload a payment screenshot first."
        )

    else:

        df = pd.DataFrame(
            st.session_state.transactions
        )

        total = df["Amount"].sum()

        count = len(df)

        c1, c2 = st.columns(2)

        c1.metric(
            "Total Expenses",
            f"₹{total:,.2f}"
        )

        c2.metric(
            "Transactions",
            count
        )

        st.subheader("Transactions")

        st.dataframe(
            df,
            use_container_width=True
        )

        st.subheader("Spending by Category")

        category_total = (
            df.groupby("Category")["Amount"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(category_total)


# -----------------------------
# AI Advice
# -----------------------------

else:

    st.header("3️⃣ Basic Financial Advice")

    if not st.session_state.transactions:

        st.info(
            "Add at least one transaction "
            "to receive advice."
        )

    else:

        df = pd.DataFrame(
            st.session_state.transactions
        )

        total = df["Amount"].sum()

        category_totals = (
            df.groupby("Category")["Amount"]
            .sum()
        )

        top_category = category_totals.idxmax()

        top_amount = category_totals.max()

        st.write("### Spending Summary")

        st.write(
            f"- Total tracked expenses: "
            f"**₹{total:,.2f}**"
        )

        st.write(
            f"- Highest spending category: "
            f"**{top_category} "
            f"(₹{top_amount:,.2f})**"
        )

        st.write("")

        st.success(
            f"💡 Basic advice: Your highest tracked "
            f"spending is in **{top_category}**. "
            f"Consider setting a monthly limit for this "
            f"category and review your expenses regularly."
        )

        st.caption(
            "Educational prototype only. "
            "It does not provide certified financial "
            "or investment advice."
        )