# Personal Money Dashboard - Setup Guide

## Quick Start

### Prerequisites
- Python 3.10 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the repository**
   ```bash
   git clone <repository-url> personal-money-dashboard
   cd personal-money-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```
   
   Or use the provided startup script:
   ```bash
   python run_app.py
   ```

4. **Access the dashboard**
   Open your web browser and go to: `http://localhost:8501`

## Data Setup

### Transaction Files
The dashboard automatically processes transaction files from the `data/raw/` directory. 

**File Naming Convention:**
```
transaction-raw-import-[bank]_[accountType]_[last4]-YYYY.MM.DD-YYYY.MM.DD.csv
```

**Examples:**
- `transaction-raw-import-boa_chk_7259-2025.04.01-2025.05.06.csv`
- `transaction-raw-import-amex_cc_1234-2025.01.01-2025.03.31.csv`

**Where:**
- `[bank]` = Bank name (e.g., boa, amex, chase)
- `[accountType]` = Account type (chk for checking, cc for credit card)
- `[last4]` = Last 4 digits of account number
- `YYYY.MM.DD` = Start and end dates of the transaction period

### Supported File Formats
- CSV files (`.csv`)
- Excel files (`.xlsx`, `.xls`) - even if they have a `.csv` extension

### Required Columns
Your transaction files should contain at least these columns:
- **Date** - Transaction date
- **Amount** - Transaction amount (positive for income, negative for expenses)
- **Description** - Transaction description

Optional columns:
- **Running Balance** - Account running balance

## Features Overview

### 📊 Reports
- **Profit & Loss** - Income vs expenses summary
- **Balance Sheet** - Assets and liabilities overview
- **Cash Flow** - Cash movement analysis
- **Comparisons** - Period-over-period comparisons

### 📈 Analytics
- **Time Series** - Trend analysis and forecasting
- **Account Details** - Individual account analysis

### 🛠️ Tools
- **Forecasting** - Future cash flow predictions
- **Subscription Tracking** - Recurring expense detection
- **Debt Payoff Calculator** - Loan payoff planning
- **List Management** - Custom lists and categories
- **Task Management** - Personal finance tasks
- **Personal Wiki/Notes** - Financial notes and documentation
- **Document Processing** - File upload and processing
- **Chatbot** - AI-powered financial assistance

### 📚 Reference
- **Reference & Resources** - Help and documentation

## Configuration

### Customizing the Dashboard
Edit `config.py` to modify:
- App title and icon
- Default user name
- Data directories
- Display settings (chart heights, table rows, etc.)

### Adding Custom Categories
Use the **List Management** tool to create custom categories and tags for better transaction organization.

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.10+ required)

2. **No Data Displayed**
   - Verify transaction files are in `data/raw/` directory
   - Check file naming convention
   - Ensure files contain required columns (Date, Amount, Description)

3. **File Reading Errors**
   - Check file format (CSV or Excel)
   - Verify file encoding (UTF-8 recommended)
   - Ensure file is not corrupted

4. **Port Already in Use**
   - Change port: `streamlit run app.py --server.port 8502`
   - Or kill existing process: `taskkill /f /im python.exe`

### Getting Help
- Check the **Reference & Resources** page in the dashboard
- Review transaction file format requirements
- Ensure all dependencies are properly installed

## Development

### Project Structure
```
personal-money-dashboard/
├── app.py                 # Main application entry point
├── config.py              # Configuration settings
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── run_app.py            # Startup script
├── data/
│   ├── raw/              # Place transaction files here
│   └── processed/        # Processed data (auto-generated)
├── modules/              # Dashboard pages
│   ├── home.py
│   ├── profit_loss.py
│   ├── balance_sheet.py
│   └── ...
└── assets/               # Static assets (images, etc.)
```

### Adding New Features
1. Create a new module in `modules/`
2. Define a `render()` function
3. Import and add to navigation in `app.py`
4. Update configuration if needed

### Extending Data Processing
Modify `utils.py` to add custom data processing functions or support for new file formats.

## License
This project is released under the MIT License.
