import pandas as pd

# Your Excel file name
EXCEL_FILE = "Paytm_UPI_Statement.xlsx"
SHEET_NAME = "Passbook Payment History"
OUTPUT_FILE = "paytm.json"

# Read Excel and convert to JSON
print(f"Reading {EXCEL_FILE}...")
df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
df.to_json(OUTPUT_FILE, orient='records', indent=2, date_format='iso')

print(f"✅ Converted {len(df)} transactions to {OUTPUT_FILE}")
print(f"Columns: {list(df.columns)}")
