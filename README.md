# AI Financial Advisor & Expense Manager — Week 4

## Overview
Week 4 Track A prototype extending the Week 1 OCR model.

### Features
- Payment screenshot OCR
- Merchant, amount and date extraction
- Rule-based expense categorization
- Manual expense entry
- CSV import
- SQLite persistent storage
- Spending dashboard and category analysis
- Monthly income and expense budget
- Personalized spending insights
- Transaction viewing and deletion
- CSV template download
- Basic validation and error handling

## Architecture
Screenshot / Manual / CSV
→ OCR or Data Parser
→ Merchant + Amount + Date
→ Categorization
→ User Verification
→ SQLite
→ Dashboard / Budget Analysis
→ Personalized Financial Insights

## Installation
1. Install Python 3.10+.
2. Run:
```bash
pip install -r requirements.txt
```
3. Install Tesseract OCR on Windows and add it to PATH.
If needed, add this after the imports in `app.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```
4. Run:
```bash
streamlit run app.py
```

## CSV format
Required columns:
```text
date,merchant,amount,category
```

Example:
```csv
date,merchant,amount,category
15/08/2026,Swiggy,450,Food
16/08/2026,Uber,220,Transport
17/08/2026,Amazon,1200,Shopping
```

## Week 4 workflow
1. Add transactions using screenshot, manual entry or CSV.
2. Verify OCR-extracted values.
3. Store transactions in SQLite.
4. View category-wise spending on the dashboard.
5. Set income and monthly budget.
6. Review personalized spending insights.

## Limitations
This is a Week 4 prototype. OCR and categorization are rule-based. The financial advisor is educational and not a certified investment advisor. No real banking credentials or live bank API is required.

## Next improvements
- LangChain + LLM advisor
- RAG using financial books/articles
- Indian personal-finance knowledge
- Better OCR confidence scoring
- Goal tracking
- Guru philosophy comparison
- Splitwise API if available
- Stronger security/privacy
- Cloud deployment

## Suggested team split
Member 1: AI/advice and future LangChain/RAG.
Member 2: OCR, extraction, categorization and database.
Member 3: Streamlit UI, analytics, testing and deployment.
