# Admin Center Guide

## Overview

The Admin Center provides powerful tools for managing transaction data, mappings, and categorization. It consists of two main pages:

1. **Transaction Mapping** - Map unmapped transactions to categories and metadata
2. **List Management** - Create and customize lists used throughout the application

## Transaction Mapping Page

### Purpose
Map unmapped transaction descriptions to categories, tags, payers, and payees using a user-friendly interface.

### Features

#### **Summary Statistics**
- Number of unmapped descriptions
- Total transaction count
- Total amount involved
- Average occurrences per description

#### **Transaction Table**
- Displays all unmapped transactions
- Shows transaction count, total amount, date range, and bank account
- Sortable by transaction count, amount, or description
- Searchable by description text

#### **Mapping Interface**
1. **Select Transaction**: Choose from dropdown of unmapped descriptions
2. **View Details**: See occurrence count, total amount, date range, and account
3. **Assign Values**: Use dropdowns to assign:
   - Account Type (income/expense/transfer)
   - Category 1, 2, 3 (hierarchical categorization)
   - Tags (multi-select for multiple tags)
   - Payer (who paid)
   - Payee (who received payment)

#### **Quick Mapping**
Pre-configured mapping patterns for common transaction types:
- **GROCERY** → Food & Dining, Groceries, essential/monthly tags
- **GAS** → Transportation, Fuel, essential/monthly tags
- **RESTAURANT** → Food & Dining, Dining Out, luxury tag
- **NETFLIX** → Entertainment, Streaming, subscription/monthly tags
- **UTILITY** → Utilities, Electricity, essential/monthly tags
- **SALARY** → Income, Salary, monthly/recurring tags

#### **Export Options**
- Export unmapped transactions to CSV
- Refresh data to see latest changes

### How to Use

1. **Review Unmapped Transactions**
   - Check the summary statistics
   - Browse the transaction table
   - Use search to find specific transactions

2. **Map Individual Transactions**
   - Select a transaction from the dropdown
   - Review transaction details
   - Assign appropriate categories, tags, payer, and payee
   - Click "Save Mapping"

3. **Use Quick Mapping**
   - Click quick mapping buttons for common patterns
   - System automatically finds and maps matching transactions

4. **Monitor Progress**
   - Refresh data to see updated statistics
   - Continue until all transactions are mapped

## List Management Page

### Purpose
Create and customize the lists used in dropdown menus throughout the application.

### Available Lists

#### **Account Types**
- income, expense, transfer, investment, loan

#### **Categories**
- Food & Dining, Transportation, Entertainment, Utilities, Healthcare, Shopping, Education, Travel, Insurance, Taxes, Investments, Gifts, Charity, Income

#### **Tags**
- essential, luxury, monthly, annual, subscription, one-time, recurring, business, personal, emergency

#### **Payers**
- Self, Employer, Bank, Investment, Government, Insurance

#### **Payees**
- Grocery Store, Gas Station, Restaurant, Utility Company, Internet Provider, Phone Company, Insurance Company, Healthcare Provider, Retail Store, Online Service

### Features

#### **Individual List Management**
- View current items in each list
- Add new items individually
- Remove items with confirmation
- Bulk add multiple items (one per line)

#### **Bulk Operations**
- **Import from CSV**: Upload CSV with columns `list_name` and `item`
- **Export to CSV**: Download all lists as CSV file

#### **Quick Add Common Items**
Pre-configured common items for each list type:
- Expandable sections for each list
- Shows only missing items
- Multi-select to add multiple items at once

### How to Use

#### **Adding Items**
1. **Individual**: Enter item name and click "Add"
2. **Bulk**: Enter multiple items (one per line) and click "Add All"
3. **Quick Add**: Use pre-configured common items

#### **Removing Items**
- Click "Remove" button next to any item
- Confirmation will update the list immediately

#### **Importing/Exporting**
1. **Export**: Click "Export Lists to CSV" to download current lists
2. **Import**: Upload CSV file with `list_name` and `item` columns

## Data Processing Workflow

### Enhanced Data Structure

The new data processing pipeline adds these columns to your transaction data:

#### **Period Columns**
- `PeriodYear`: YYYY format (e.g., "2025")
- `PeriodMonth`: MM-YYYY format (e.g., "01-2025")
- `PeriodQuarter`: Q0-YYYY format (e.g., "Q1-2025")

#### **Bank Information**
- `Bank`: Bank name extracted from filename
- `AccountType`: Account type (CHK/CC) from filename
- `AccountLast4`: Last 4 digits from filename
- `BankAccount`: Combined identifier (e.g., "BOA CHK 7259")

#### **Mapping Columns**
- `AccountType`: Mapped account type
- `Category1`, `Category2`, `Category3`: Hierarchical categories
- `Tags`: List of tags
- `Payer`: Who made the payment
- `Payee`: Who received the payment
- `MappedDescription`: The description used for mapping

#### **Data Quality**
- `IsDuplicate`: Flag for duplicate transactions
- `TransactionType`: Incoming/Outgoing based on amount

### File Naming Convention

Transaction files must follow this pattern:
```
transaction-raw-import-[bank]_[type]_[last4]-YYYY.MM.DD-YYYY.MM.DD.csv
```

**Examples:**
- `transaction-raw-import-boa_chk_7259-2025.04.01-2025.05.06.csv`
- `transaction-raw-import-amex_cc_1234-2025.01.01-2025.03.31.csv`

### Mapping Strategy

The system uses intelligent matching:
1. **Exact Match**: Perfect description match
2. **Partial Match**: Case-insensitive substring matching
3. **Fuzzy Match**: Similarity-based matching (60% threshold)

### Duplicate Detection

Duplicates are detected using a composite key:
- Date + Amount + Description + Bank + AccountLast4
- First occurrence is kept, subsequent are marked as duplicates

## Best Practices

### **Mapping Transactions**
1. Start with high-frequency transactions
2. Use consistent naming for similar transactions
3. Leverage quick mapping for common patterns
4. Review and refine mappings over time

### **Managing Lists**
1. Keep categories broad but meaningful
2. Use tags for detailed classification
3. Maintain consistent naming conventions
4. Export lists regularly for backup

### **Data Quality**
1. Ensure consistent file naming
2. Check for duplicate transactions
3. Review unmapped transactions regularly
4. Validate mapping accuracy

## Troubleshooting

### **Common Issues**

#### **No Unmapped Transactions**
- All transactions are already mapped
- Check if transaction files are in the correct location
- Verify file naming convention

#### **Mapping Not Applied**
- Refresh the page to see updates
- Check if mapping was saved successfully
- Verify transaction descriptions match exactly

#### **Import Errors**
- Ensure CSV has correct column names
- Check for special characters in data
- Verify file encoding (UTF-8 recommended)

#### **Performance Issues**
- Large datasets may take time to process
- Use search/filter to work with smaller subsets
- Consider breaking large files into smaller chunks

### **Getting Help**
- Check the transaction mapping interface for unmapped items
- Review the mapping file structure in `data/processed/transaction_mappings.json`
- Export and review your current mappings
- Use the quick mapping features for common patterns

## File Locations

### **Data Files**
- Raw transactions: `data/raw/`
- Processed data: `data/processed/transactions_combined_enhanced.csv`
- Mappings: `data/processed/transaction_mappings.json`

### **Backup Recommendations**
- Export mappings regularly
- Keep copies of raw transaction files
- Document any custom categories or tags

## Future Enhancements

The Admin Center is designed to be extensible. Future versions may include:
- Advanced fuzzy matching algorithms
- Machine learning for automatic categorization
- Bulk mapping operations
- Mapping templates and presets
- Integration with external categorization services
