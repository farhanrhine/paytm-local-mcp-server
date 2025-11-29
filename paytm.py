import os
import sqlite3
import json
from fastmcp import FastMCP

# Database path - stores all Paytm transactions
DB_PATH = os.path.join(os.path.dirname(__file__), "paytm.db")

# JSON file path (converted from Excel) - used as resource
PAYTM_JSON_PATH = os.path.join(os.path.dirname(__file__), "paytm.json")

mcp = FastMCP("PaytmTracker")


def init_db():
    """Initialize the database with paytm_transactions table based on Paytm columns."""
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS paytm_transactions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                time TEXT DEFAULT '',
                transaction_details TEXT NOT NULL,
                other_details TEXT DEFAULT '',
                account_id TEXT DEFAULT '',
                amount REAL NOT NULL,
                upi_ref_no TEXT DEFAULT '',
                order_id TEXT DEFAULT '',
                remarks TEXT DEFAULT '',
                tags TEXT DEFAULT '',
                comments TEXT DEFAULT ''
            )
        """)


# Initialize database on module load
init_db()


# ============ RESOURCE - Paytm JSON Data ============

@mcp.resource("paytm://transactions", mime_type="application/json")
def paytm_transactions_resource():
    """Read Paytm transactions from JSON file as a resource."""
    with open(PAYTM_JSON_PATH, "r", encoding="utf-8") as f:
        return f.read()


# ============ TOOLS ============

@mcp.tool()
def import_paytm_data():
    """Import Paytm transactions from JSON resource into database."""
    try:
        # Read JSON file
        with open(PAYTM_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with sqlite3.connect(DB_PATH) as conn:
            # Clear existing data
            conn.execute("DELETE FROM paytm_transactions")
            
            # Insert each transaction
            for row in data:
                # Parse amount - handle string format like "-30.00" or "500.00"
                amount_str = str(row.get('Amount', '0')).replace(',', '')
                try:
                    amount = float(amount_str)
                except:
                    amount = 0.0
                
                # Parse date - convert DD/MM/YYYY to YYYY-MM-DD
                date_str = str(row.get('Date', ''))
                if '/' in date_str:
                    parts = date_str.split('/')
                    if len(parts) == 3:
                        date_str = f"{parts[2]}-{parts[1]}-{parts[0]}"
                
                conn.execute("""
                    INSERT INTO paytm_transactions 
                    (date, time, transaction_details, other_details, account_id, 
                     amount, upi_ref_no, order_id, remarks, tags, comments)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    date_str,
                    str(row.get('Time', '') or ''),
                    str(row.get('Transaction Details', '') or ''),
                    str(row.get('Other Transaction Details (UPI ID or A/c No)', '') or ''),
                    str(row.get('Your Account', '') or ''),  # Correct column name
                    amount,
                    str(row.get('UPI Ref No.', '') or ''),
                    str(row.get('Order ID', '') or ''),
                    str(row.get('Remarks', '') or ''),
                    str(row.get('Tags', '') or ''),
                    str(row.get('Comment', '') or '')  # Correct column name (singular)
                ))
            
            count = conn.execute("SELECT COUNT(*) FROM paytm_transactions").fetchone()[0]
        
        return {"status": "success", "imported": count}
    except FileNotFoundError:
        return {"status": "error", "message": "paytm_data.json not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def get_paytm_summary():
    """Get summary of Paytm transactions (total spent, received, net)."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            total = conn.execute("SELECT COUNT(*) FROM paytm_transactions").fetchone()[0]
            credit = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM paytm_transactions WHERE amount > 0").fetchone()[0]
            debit = conn.execute("SELECT COALESCE(SUM(ABS(amount)), 0) FROM paytm_transactions WHERE amount < 0").fetchone()[0]
        
        return {
            "total_transactions": total,
            "total_received": float(credit),
            "total_spent": float(debit),
            "net": float(credit - debit)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def search_paytm(keyword: str):
    """Search Paytm transactions by keyword."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute('''
                SELECT * FROM paytm_transactions 
                WHERE transaction_details LIKE ? 
                   OR other_details LIKE ?
                   OR remarks LIKE ?
                ORDER BY date DESC
            ''', (f'%{keyword}%',) * 3)
            results = [dict(row) for row in cur.fetchall()]
        
        return {"found": len(results), "transactions": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def get_paytm_by_date(date: str):
    """Get Paytm transactions for a specific date (YYYY-MM-DD)."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute('''
                SELECT * FROM paytm_transactions 
                WHERE date LIKE ? ORDER BY time DESC
            ''', (f'%{date}%',))
            results = [dict(row) for row in cur.fetchall()]
        
        return {"date": date, "count": len(results), "transactions": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def get_top_merchants(limit: int = 10):
    """Get top merchants by total amount."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute('''
                SELECT transaction_details as merchant,
                       COUNT(*) as count,
                       SUM(ABS(amount)) as total
                FROM paytm_transactions 
                GROUP BY transaction_details
                ORDER BY total DESC LIMIT ?
            ''', (limit,))
            results = [dict(row) for row in cur.fetchall()]
        
        return {"top_merchants": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def get_monthly_summary():
    """Get month-wise summary of transactions."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute('''
                SELECT strftime('%Y-%m', date) as month,
                       COUNT(*) as count,
                       SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as received,
                       SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as spent
                FROM paytm_transactions 
                GROUP BY month ORDER BY month DESC
            ''')
            results = [dict(row) for row in cur.fetchall()]
        
        return {"monthly_summary": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    mcp.run()