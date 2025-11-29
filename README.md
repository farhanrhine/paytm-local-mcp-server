# 💳 Paytm UPI Statement Analyzer

> Query your Paytm UPI transactions using natural language with Claude AI - 100% local, privacy-first.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 What is this?

A simple MCP (Model Context Protocol) server that lets you analyze your Paytm UPI transaction history by asking Claude questions in plain English. All your financial data stays on your machine - no cloud uploads!

**Ask questions like:**
- "How much did I spend this month?"
- "Show my top 10 merchants"
- "Search for Swiggy transactions"
- "What's my monthly spending breakdown?"

---

## 🔄 How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WORKFLOW                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
  │   PAYTM APP  │      │    EXCEL     │      │     JSON     │
  │              │ ───► │   Statement  │ ───► │    File      │
  │  📱 Export   │      │   📊 .xlsx   │      │   📄 .json   │
  └──────────────┘      └──────────────┘      └──────────────┘
                                                     │
                        ┌────────────────────────────┘
                        ▼
  ┌──────────────────────────────────────────────────────────────────────────┐
  │                         MCP SERVER (paytm.py)                             │
  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐       │
  │  │  📥 Import Tool │    │  🔍 Query Tools │    │  📊 SQLite DB   │       │
  │  │                 │───►│                 │◄──►│                 │       │
  │  │ JSON → Database │    │ Search, Summary │    │ paytm.db        │       │
  │  └─────────────────┘    │ Top Merchants   │    └─────────────────┘       │
  │                         │ Monthly View    │                               │
  │                         └─────────────────┘                               │
  └──────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
  ┌──────────────────────────────────────────────────────────────────────────┐
  │                         CLAUDE DESKTOP                                    │
  │                                                                           │
  │   You: "How much did I spend on Swiggy?"                                 │
  │                                                                           │
  │   Claude: "You spent ₹8,500 on Swiggy across 42 transactions.            │
  │            Your average order was ₹202."                                 │
  │                                                                           │
  └──────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
fastmcp_expence_tracker/
├── paytm.py              # 🔧 MCP Server - main file
├── convert_to_json.py    # 🔄 Excel to JSON converter
├── paytm_data.json       # 📄 Your transaction data (generated)
├── paytm.db              # 🗄️ SQLite database (generated)
└── README.md             # 📖 This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [Claude Desktop](https://claude.ai/download) installed

---

### Step 0: Install UV & FastMCP

```bash
# Install UV (Python package manager)
pip install uv

# Initialize project (if starting fresh)
uv init .

# Add FastMCP dependency
uv add fastmcp

# Verify installation
uv run fastmcp version or fastmcp version
```

---

### Step 1: Export Your Paytm Statement

1. Open **Paytm App**
2. Go to **Passbook** → **UPI** 
3. Tap **Download Statement**
4. Select date range (last 6 months recommended)
5. Download as **Excel (.xlsx)**
6. Save to this folder

### Step 2: Convert Excel to JSON

```bash
# Install the openpyxl library which is required to read Excel files.
pip install openpyxl
# Edit convert_to_json.py with your file name
python convert_to_json.py
```

**Output:** `paytm.json` with all your transactions

### Step 3: Run & Install MCP Server

```bash
# Test the server locally (optional)
uv run fastmcp run paytm.py

# Install in Claude Desktop
uv run fastmcp install claude-desktop paytm.py
```

This adds the server to Claude Desktop's config file automatically.

### Step 4: Restart Claude Desktop

Close and reopen Claude Desktop completely.

### Step 5: Start Querying!

In Claude Desktop, type:
```
Import my Paytm data or add as resource from claude desktop + button something name appears like add from PaytmTracker
```

Then ask anything:
```
Show my spending summary
Who are my top 5 merchants?
Search for Amazon
Show November spending
```

---

## 🛠️ Available Tools

| Tool | Description | Example Query |
|------|-------------|---------------|
| `import_paytm_data` | Load JSON into database | "Import my Paytm data" |
| `get_paytm_summary` | Total spent/received/net | "Show my summary" |
| `search_paytm` | Search by keyword | "Search for Swiggy" |
| `get_paytm_by_date` | Transactions for a date | "What did I spend on 2025-11-15?" |
| `get_top_merchants` | Top spenders by amount | "Top 10 merchants" |
| `get_monthly_summary` | Month-wise breakdown | "Monthly spending" |

---


## 📊 Data Format

Your Paytm Excel has these columns:

| Column | Example | In Database |
|--------|---------|-------------|
| Date | 28/11/2025 | 2025-11-28 |
| Time | 18:34:46 | 18:34:46 |
| Transaction Details | Paid to Swiggy | transaction_details |
| Amount | -245.00 | -245.0 (float) |
| UPI Ref No. | 53xxxxxxxxx | upi_ref_no |
| Tags | #🛒 Groceries | tags |

---

## 🔒 Privacy

✅ **100% Local** - All data stays on your computer  
✅ **No Cloud** - Nothing uploaded anywhere  
✅ **No API Keys** - Uses free Claude Desktop  
✅ **You Control** - Delete anytime  

---

## 🗺️ Roadmap

### v1.0 (Current) - Basic Version
- [x] Import Paytm Excel statements
- [x] Search transactions
- [x] Summary statistics
- [x] Top merchants
- [x] Monthly breakdown

### v2.0 (Coming Soon) - Advanced Version
- [ ] 📊 Visual Dashboard (React + Charts)
- [ ] 📱 PhonePe support
- [ ] 📱 Google Pay support
- [ ] 🏦 Bank statement support
- [ ] 📈 Spending trends & predictions
- [ ] 🏷️ Smart categorization
- [ ] 💰 Budget tracking
- [ ] 📤 Export reports

---

## 🔧 Troubleshooting

**"MCP server not showing in Claude"**
```bash
# Fully close Claude Desktop
taskkill /IM "Claude.exe" /F

# Reinstall
fastmcp install claude-desktop paytm.py

# Reopen Claude
```

**"Import failed"**
- Check `paytm.json` exists
- Verify JSON format is correct
- Check column names match

**"No transactions found"**
- Run "Import my Paytm data" first
- Check `paytm.db` was created

---

## 📄 License

MIT License - Use freely!

---

## 🙏 Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) - Easy MCP server creation
- [Model Context Protocol](https://modelcontextprotocol.io/) - By Anthropic

---

**Made with Farhan**

⭐ Star this repo if it helped you!
