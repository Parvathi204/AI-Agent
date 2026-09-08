import streamlit as st
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re
import pandas as pd
import sqlite3
from datetime import datetime

st.set_page_config(page_title="AI Financial Advisor - Week 4", page_icon="💰", layout="wide")

DB_NAME = "financial_advisor.db"
CATEGORIES = ["Food","Transport","Shopping","Groceries","Entertainment","Bills","Healthcare","Education","Rent","Others"]

def db():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = db()
    conn.execute("""CREATE TABLE IF NOT EXISTS transactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL, merchant TEXT NOT NULL, amount REAL NOT NULL,
        category TEXT NOT NULL, source TEXT NOT NULL, created_at TEXT NOT NULL)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS settings(
        key TEXT PRIMARY KEY, value TEXT)""")
    conn.commit(); conn.close()

def save_transaction(date, merchant, amount, category, source):
    conn = db()
    conn.execute("""INSERT INTO transactions
        (date,merchant,amount,category,source,created_at)
        VALUES(?,?,?,?,?,?)""",
        (date, merchant, float(amount), category, source,
         datetime.now().isoformat(timespec="seconds")))
    conn.commit(); conn.close()

def load_transactions():
    conn = db()
    df = pd.read_sql_query(
        "SELECT id,date,merchant,amount,category,source FROM transactions ORDER BY id DESC", conn)
    conn.close()
    return df

def delete_transaction(tid):
    conn = db()
    conn.execute("DELETE FROM transactions WHERE id=?", (int(tid),))
    conn.commit(); conn.close()

def get_setting(key, default="0"):
    conn = db()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row[0] if row else default

def save_setting(key, value):
    conn = db()
    conn.execute("""INSERT INTO settings(key,value) VALUES(?,?)
                    ON CONFLICT(key) DO UPDATE SET value=excluded.value""",
                 (key, str(value)))
    conn.commit(); conn.close()

init_db()

def preprocess_image(image):
    image = image.convert("L")
    image = ImageEnhance.Contrast(image).enhance(2.0)
    return image.filter(ImageFilter.SHARPEN)

def extract_amount(text):
    patterns = [
        r'(?:₹|Rs\.?|INR)\s*([0-9,]+(?:\.[0-9]{1,2})?)',
        r'(?:amount|paid|total|debit|spent|payment)\s*[:\-]?\s*(?:₹|Rs\.?|INR)?\s*([0-9,]+(?:\.[0-9]{1,2})?)'
    ]
    values = []
    for p in patterns:
        for x in re.findall(p, text, flags=re.I):
            try: values.append(float(x.replace(",", "")))
            except ValueError: pass
    return values[-1] if values else None

def extract_date(text):
    for p in [r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
              r'\b(\d{2,4}[/-]\d{1,2}[/-]\d{1,2})\b']:
        m = re.search(p, text)
        if m: return m.group(1)
    return datetime.now().strftime("%d/%m/%Y")

def extract_merchant(text):
    known = ["swiggy","zomato","uber","ola","rapido","amazon","flipkart",
             "myntra","dmart","blinkit","zepto","netflix","spotify",
             "google pay","phonepe","paytm"]
    low = text.lower()
    for x in known:
        if x in low: return x.title()
    ignored = ["transaction","successful","success","paid","payment","date","amount","upi","reference"]
    for line in [x.strip() for x in text.splitlines() if x.strip()]:
        if 3 <= len(line) <= 50 and not re.search(r'\d{3,}', line) and not any(w in line.lower() for w in ignored):
            return line
    return "Unknown"

def categorize(merchant, text):
    combined = f"{merchant} {text}".lower()
    rules = {
        "Food":["swiggy","zomato","restaurant","food","domino","pizza","cafe","hotel"],
        "Transport":["uber","ola","rapido","metro","bus","petrol","fuel","auto","cab"],
        "Shopping":["amazon","flipkart","myntra","shopping","clothing","fashion"],
        "Groceries":["dmart","blinkit","zepto","grocery","groceries"],
        "Entertainment":["netflix","spotify","movie","cinema","game"],
        "Bills":["electricity","recharge","internet","mobile","bill","utility"],
        "Healthcare":["hospital","pharmacy","medical","medicine","clinic","doctor"],
        "Education":["college","course","book","education","tuition"],
        "Rent":["rent","house rent","room rent"]
    }
    for cat, words in rules.items():
        if any(w in combined for w in words): return cat
    return "Others"

def personalized_advice(df, income, budget):
    if df.empty: return "Add expenses to receive spending insights."
    total = df.amount.sum()
    cats = df.groupby("category").amount.sum().sort_values(ascending=False)
    top_cat, top_amt = cats.index[0], cats.iloc[0]
    advice = []
    if income > 0:
        savings = income - total
        rate = savings / income * 100
        advice.append(
            f"Your tracked savings are ₹{savings:,.2f} ({rate:.1f}% of income)."
            if savings >= 0 else
            f"⚠️ Tracked expenses exceed income by ₹{abs(savings):,.2f}."
        )
    if budget > 0:
        advice.append(
            f"⚠️ You exceeded the overall budget by ₹{total-budget:,.2f}."
            if total > budget else
            f"You have ₹{budget-total:,.2f} remaining in the overall budget."
        )
    discretionary = cats[cats.index.isin(["Food","Shopping","Entertainment"])].sum()
    if total and discretionary / total >= .30:
        advice.append("Food, shopping and entertainment form a significant share of spending. Consider setting category limits.")
    advice.append(f"Highest tracked spending: {top_cat} at ₹{top_amt:,.2f}. Review this category first.")
    return "\n\n".join(advice)

st.sidebar.title("💰 Financial Advisor")
st.sidebar.caption("Week 4 Working Prototype")
page = st.sidebar.radio("Navigation", ["Dashboard","Upload Screenshot","Manual Expense","CSV Upload","Budget & Advice","Transactions"])

if page == "Dashboard":
    st.title("📊 Financial Dashboard")
    df = load_transactions()
    if df.empty:
        st.info("No transactions yet. Add an expense first.")
    else:
        total = df.amount.sum(); count = len(df); avg = df.amount.mean()
        income = float(get_setting("monthly_income","0") or 0)
        savings = income-total if income > 0 else None
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Total Expenses",f"₹{total:,.2f}")
        c2.metric("Transactions",count)
        c3.metric("Average Expense",f"₹{avg:,.2f}")
        c4.metric("Estimated Savings",f"₹{savings:,.2f}" if savings is not None else "Set Income")
        left,right = st.columns(2)
        with left:
            st.subheader("Spending by Category")
            st.bar_chart(df.groupby("category").amount.sum().sort_values(ascending=False))
        with right:
            s=df.groupby("category").amount.sum().sort_values(ascending=False)
            st.subheader("Category Percentage")
            st.dataframe(pd.DataFrame({"Amount (₹)":s.round(2),"Percentage (%)":(s/total*100).round(1)}),use_container_width=True)
        st.subheader("Recent Transactions")
        st.dataframe(df.head(10),use_container_width=True)

elif page == "Upload Screenshot":
    st.title("📷 Screenshot Expense Extraction")
    uploaded = st.file_uploader("Choose a payment screenshot",type=["png","jpg","jpeg"])
    if uploaded:
        image=Image.open(uploaded)
        st.image(image,caption="Uploaded Screenshot",use_container_width=True)
        if st.button("🔍 Extract Transaction",type="primary"):
            try:
                text=pytesseract.image_to_string(preprocess_image(image))
            except Exception:
                text=""
                st.error("OCR could not run. Install Tesseract OCR and add it to PATH.")
            st.subheader("OCR Result")
            st.text_area("Extracted Text",text,height=180)
            amount=extract_amount(text); date=extract_date(text)
            merchant=extract_merchant(text); category=categorize(merchant,text)
            st.divider(); st.subheader("✏️ Verify Extracted Transaction")
            c1,c2=st.columns(2)
            with c1:
                merchant_edit=st.text_input("Merchant",merchant)
                amount_edit=st.number_input("Amount (₹)",min_value=0.0,value=float(amount or 0),step=10.0)
            with c2:
                date_edit=st.text_input("Date",date)
                category_edit=st.selectbox("Category",CATEGORIES,index=CATEGORIES.index(category))
            if amount is None: st.warning("Amount was not confidently detected. Please verify it manually.")
            if st.button("✅ Confirm & Save",type="primary"):
                if not merchant_edit.strip(): st.error("Merchant is required.")
                elif amount_edit<=0: st.error("Enter a valid amount.")
                else:
                    save_transaction(date_edit,merchant_edit.strip(),amount_edit,category_edit,"Screenshot/OCR")
                    st.success("Transaction saved successfully!")

elif page == "Manual Expense":
    st.title("✍️ Manual Expense Entry")
    with st.form("manual"):
        c1,c2=st.columns(2)
        with c1:
            date=st.date_input("Date"); merchant=st.text_input("Merchant / Description")
            amount=st.number_input("Amount (₹)",min_value=0.0,step=10.0)
        with c2:
            category=st.selectbox("Category",CATEGORIES)
            source=st.selectbox("Source",["Manual Entry","UPI","Bank Statement","Splitwise"])
        submit=st.form_submit_button("➕ Add Expense",type="primary")
    if submit:
        if not merchant.strip(): st.error("Merchant is required.")
        elif amount<=0: st.error("Amount must be greater than ₹0.")
        else:
            save_transaction(date.strftime("%d/%m/%Y"),merchant.strip(),amount,category,source)
            st.success("Expense added successfully!")

elif page == "CSV Upload":
    st.title("📄 CSV Expense Import")
    st.write("Required columns: date, merchant, amount, category.")
    template=pd.DataFrame({"date":["15/08/2026","16/08/2026"],"merchant":["Swiggy","Uber"],"amount":[450,220],"category":["Food","Transport"]})
    st.download_button("⬇️ Download CSV Template",template.to_csv(index=False).encode(),"expense_template.csv","text/csv")
    uploaded=st.file_uploader("Upload CSV",type=["csv"])
    if uploaded:
        try:
            df=pd.read_csv(uploaded); df.columns=[c.strip().lower() for c in df.columns]
            st.dataframe(df.head(10),use_container_width=True)
            required={"date","merchant","amount","category"}; missing=required-set(df.columns)
            if missing: st.error("Missing columns: "+", ".join(sorted(missing)))
            else:
                df.amount=pd.to_numeric(df.amount,errors="coerce")
                valid=df.dropna(subset=["date","merchant","amount","category"]).copy()
                if st.button("📥 Import Transactions",type="primary"):
                    for _,r in valid.iterrows():
                        if float(r.amount)>0:
                            save_transaction(str(r.date),str(r.merchant),float(r.amount),str(r.category) if str(r.category) in CATEGORIES else "Others","CSV")
                    st.success(f"{len(valid)} transactions imported successfully.")
        except Exception as e: st.error(f"Could not process CSV: {e}")

elif page == "Budget & Advice":
    st.title("🎯 Budget & Personalized Advice")
    df=load_transactions()
    income0=float(get_setting("monthly_income","0") or 0); budget0=float(get_setting("monthly_budget","0") or 0)
    with st.form("settings"):
        income=st.number_input("Monthly Income (₹)",min_value=0.0,value=income0,step=1000.0)
        budget=st.number_input("Monthly Expense Budget (₹)",min_value=0.0,value=budget0,step=1000.0)
        save=st.form_submit_button("💾 Save Budget Settings",type="primary")
    if save:
        save_setting("monthly_income",income); save_setting("monthly_budget",budget); st.success("Budget settings saved.")
    if not df.empty:
        total=df.amount.sum()
        c1,c2,c3=st.columns(3)
        c1.metric("Tracked Expenses",f"₹{total:,.2f}")
        c2.metric("Budget Remaining",f"₹{budget-total:,.2f}" if budget else "Not Set")
        c3.metric("Income - Expenses",f"₹{income-total:,.2f}" if income else "Not Set")
        if budget:
            st.progress(min(total/budget,1.0)); st.caption(f"Budget used: {total/budget*100:.1f}%")
        st.subheader("💡 Financial Insights"); st.info(personalized_advice(df,income,budget))
    else: st.info("Add transactions first.")

else:
    st.title("🧾 Transaction Manager")
    df=load_transactions()
    if df.empty: st.info("No transactions available.")
    else:
        st.dataframe(df,use_container_width=True)
        tid=st.number_input("Transaction ID to delete",min_value=1,step=1)
        if st.button("🗑️ Delete Transaction"):
            if tid in df.id.values:
                delete_transaction(tid); st.success("Transaction deleted."); st.rerun()
            else: st.error("Transaction ID not found.")

st.sidebar.divider()
st.sidebar.caption("Educational prototype • INR focused")
