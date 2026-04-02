# 💳 Paytm UPI Statement Analyzer

> Query your Paytm UPI transactions using natural language with Claude AI - 100% local, privacy-first.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
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

## 🧩 MCP Roles (Host, Client, Server, LLM)

When you run this project locally:

- **MCP Server**: `paytm.py` (FastMCP) exposes tools over MCP.
- **Client**: `clients.py` connects to the server and calls tools.
- **LLM**: Groq model (e.g., `qwen/qwen3-32b`) used by the client.
- **Host**: the app that drives the conversation. If you run `clients.py`, your terminal app is the host. If you use Claude Desktop or Copilot Chat, those become the host instead.

---

## 🔗 LangChain + LangGraph Roles

In this project:

- **LangChain**: builds the agent and connects the LLM to MCP tools.
- **LangGraph**: runs the agent as a graph (model step → tool step → model step) with state and streaming.

### How the parts connect

1. You type a message in the host (terminal running `clients.py`).
2. LangChain `create_agent` receives the message and decides whether to call tools.
3. LangGraph executes the agent loop and tool calls.
4. Tools are executed by the MCP server in `paytm.py`.
5. The final response is returned to the host and printed.

## 📁 Project Structure

```
paytm-mcp-server/
├── paytm.py              # 🔧 MCP Server - main file
├── clients.py            # 🤖 LangGraph + Groq chat client
├── convert_to_json.py    # 🔄 Excel to JSON converter
├── paytm.json            # 📄 Your transaction data (generated)
├── paytm.db              # 🗄️ SQLite database (generated)
├── pyproject.toml        # 📦 Dependencies
└── README.md             # 📖 This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
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
2. Go to **Balance & History** → **Click three dots (⋮) in top right** 
3. Tap **Download UPI Statement**
4. Select date range (last 6 months recommended) 
5. Download as **Excel (.xlsx)**
6. Save to this folder

### Step 2: Convert Excel to JSON

```bash
# Install the openpyxl library which is required to read Excel files.
uv add openpyxl
# Edit convert_to_json.py with your file name
uv run convert_to_json.py
```

**Output:** `paytm.json` with all your transactions

### Step 3: Run & Install MCP Server

```bash
# Test the server locally (optional)
uv run fastmcp run paytm.py

# Optional: install in Claude Desktop
uv run fastmcp install claude-desktop paytm.py
```

### Step 3.1: Run the Chat Client (langchain & LangGraph + Groq)

```bash
# Ensure GROQ_API_KEY is set in your environment or .env
uv run clients.py
```

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

## 🧪 MCP Inspector (Web UI)

You can inspect tools via the MCP Inspector.

### Option A: SSE (recommended)

1. Start the server:

```bash
uv run fastmcp run paytm.py
```

2. Start Inspector:

```bash
npx @modelcontextprotocol/inspector
```

3. In the Inspector UI:
- Transport Type: `SSE`
- Server URL: `http://127.0.0.1:8000/sse`

### Option B: STDIO (via uv)

Use this when `fastmcp` is not on your PATH.

- Transport Type: `STDIO`
- Command: `uv`
- Arguments: `run fastmcp run paytm.py --no-banner`


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

### v1.0 (Current) - Version
- [x] Import Paytm Excel statements
- [x] Search transactions
- [x] Summary statistics
- [x] Top merchants
- [x] Monthly breakdown
- [x] Local chat client (LangChain + LangGraph + Groq)

### v1.1 (Planned) - MCP App Features
- [ ] MCP app packaging (single host app for server + client)
- [ ] Server-side prompts for consistent tool behavior
- [ ] Authentication for MCP tool access
- [ ] Per-user profiles and permissions
- [ ] Built-in tool usage logs / audit trail

### v1.2 (Planned) - Advanced Agent Features
- [ ] Dynamic tool filtering (limit tools by context)
- [ ] Streaming UI (web chat with live tool call status)
- [ ] Scheduled reports (weekly/monthly summaries)
- [ ] Export reports (CSV, PDF)



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

**Made by Farhan**

