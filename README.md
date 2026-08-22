# AI Financial Advisor & Expense Manager — Week 1 Prototype

## What this prototype does

1. Upload a payment screenshot.
2. Run OCR using Tesseract.
3. Detect merchant, amount and date using simple rules.
4. Categorize the expense.
5. Allow the user to correct extracted information.
6. Save the transaction during the current session.
7. Display a basic spending dashboard.
8. Generate simple educational financial advice.

## Tech Stack

- Python
- Streamlit
- Tesseract OCR
- Pillow
- Pandas

## Installation

### 1. Install Python packages

```bash
pip install -r requirements.txt
```

### 2. Install Tesseract OCR

Windows:
- Install Tesseract OCR separately.
- Add the Tesseract installation folder to PATH.

If PATH is not configured, add this near the top of `app.py`:

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

### 3. Run

```bash
streamlit run app.py
```

## Week 1 Architecture

Screenshot
    ↓
OCR
    ↓
Raw text
    ↓
Regex/rule-based extraction
    ↓
Merchant + Amount + Date
    ↓
Expense categorization
    ↓
Streamlit dashboard
    ↓
Basic financial advice

## Important limitation

This is a Week 1 prototype. Transactions are stored only in Streamlit session state and are not permanently saved.

For Week 2/3, replace the temporary storage with SQLite and improve OCR/extraction accuracy.
