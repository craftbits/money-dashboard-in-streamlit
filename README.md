<!--
  Personal Money Dashboard
  -----------------------

  This README introduces the Personal Money Dashboard application. It provides an
  overview of the project, installation instructions, and guidance on how to
  use and extend the platform. The project is inspired by the open‑source
  “Real Estate Dashboard” and follows a similar design and modular structure.
-->

# Personal Money Dashboard

The **Personal Money Dashboard** is a modern, Streamlit‑based web application
designed to help individuals track their finances with ease. It consolidates
transaction data from multiple bank accounts and credit cards, cleans and
standardizes that data, and offers interactive reports, analytics, and
productivity tools. Built on top of the `real‑estate-dashboard-streamlit`
repository, this dashboard maintains the clean design and intuitive navigation
of the original while tailoring the functionality to personal finance.

## Key Features

This dashboard provides a comprehensive suite of tools to manage and analyse
personal finances:

- **Unified data ingestion** – Upload raw transaction files (in `.csv` or
  disguised Excel format) following a consistent naming convention (e.g.
  `transactions-raw-import-boa_cc_1234-2025.01.01-2025.03.31.csv`). The
  application automatically reads, cleans, and consolidates these files.
- **Profit & loss reports** – Summarise income and expenses over selected date
  ranges with optional grouping by account, category, or other dimensions.
- **Balance sheet and cash flow statements** – Approximate assets and
  liabilities, display running balances, and compare net cash movements over
  months, quarters, or years.
- **Time‑series analysis** – Chart key metrics (cash, assets, liabilities,
  net worth, income, expenses) over time and drill into specific accounts.
- **Comparisons and forecasting** – Compare current performance against budgets
  or historical periods. Forecast future cash positions with adjustable
  parameters.
- **Subscription tracking** – Detect recurring expenses and visualise them
  for better awareness and budgeting.
- **Debt payoff calculator** – Model payoff schedules for liabilities based on
  interest rates and payment plans.
- **Productivity tools** – Manage to‑do lists, custom lists (accounts,
  categories, tags), personal notes/wiki, and document uploads. A simple
  chat interface is provided as a starting point for future AI integration.
- **Extensible architecture** – Written in modular Python modules under
  `personal_money_dashboard/modules`, making it easy to extend or replace
  individual pages.

## Installation

Before running the application, ensure you have **Python 3.10+** installed.
Then follow these steps:

```bash
# 1. Clone or download the repository
git clone <repository-url> personal-money-dashboard
cd personal-money-dashboard

# 2. (Optional but recommended) create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# 3. Install dependencies
pip install --upgrade pip
pip install streamlit pandas numpy matplotlib seaborn

# 4. Run the application
streamlit run personal_money_dashboard/app.py
```

Additional libraries may be required depending on which optional features you
enable (for example, `openpyxl` for Excel files). You can install them as
needed with `pip install <library>`.

## Usage

1. **Prepare your transaction files**: Rename your raw bank or credit card
   statements to match the convention
   `transactions-raw-import-[bank]_[chk/cc]_[last4]-YYYY.MM.DD-YYYY.MM.DD.csv`.
   Place these files in the directory `personal_money_dashboard/data/raw/`.
2. **Launch the app**: Use the `streamlit run` command shown above. The
   dashboard will automatically detect and process any new files when the
   application starts.
3. **Navigate the dashboard**: Pages are grouped into categories (Home,
   Reports, Analytics, Tools, Reference). Use the sidebar to select the
   desired section. Many pages include date pickers, account selectors, and
   dropdown menus – adjust these controls to filter your data.
4. **Export your data**: Most reports provide options to download tables to
   CSV or Excel for offline analysis or record‑keeping.

## Repository Structure

```
personal-money-dashboard/
├── personal_money_dashboard/
│   ├── app.py             # Main Streamlit application orchestrating pages
│   ├── config.py          # Centralised configuration (titles, paths, UI)
│   ├── utils.py           # Utility functions (data loading, styling, etc.)
│   ├── assets/            # Images and static assets
│   ├── data/
│   │   ├── raw/           # Place raw transaction files here
│   │   └── processed/     # Automatically populated cleaned data
│   └── modules/           # Modular pages and feature implementations
│       ├── home.py
│       ├── profit_loss.py
│       ├── balance_sheet.py
│       └── ...
├── README.md              # You are here
└── personal_money_dashboard.zip # Compressed distribution (optional)
```

## Extending the Dashboard

The modular design allows you to add new pages easily:

1. **Create a new module** under `personal_money_dashboard/modules/`, e.g.
   `my_feature.py`. Define a function named `render()` that accepts a
   dataframe or reads data internally. Implement your Streamlit page logic
   inside this function.
2. **Import your module** in `app.py` and add it to the appropriate group in
   the sidebar. See how existing modules are imported and integrated for
   guidance.
3. **Update the config** in `config.py` if you need new paths, colours, or
   other parameters.

## Contributing

This project welcomes contributions! If you have ideas for new features,
improvements, or bug fixes, please open an issue or submit a pull request.

## License

This project is released under the MIT License. See `LICENSE` for details.

## Acknowledgements

This application draws inspiration from and reuses layout ideas from the
open‑source [Real Estate Dashboard](https://github.com/craftbits/real-estate-dashboard-streamlit).
Thank you to the original authors for their excellent work and design.