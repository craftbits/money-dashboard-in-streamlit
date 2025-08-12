"""
Enhanced Data Processing Pipeline for Personal Money Dashboard.

This module handles the complete data processing workflow:
1. Read all raw transaction files
2. Clean and normalize data
3. Extract metadata from filenames
4. Apply mappings from JSON file
5. Add formatted period columns
6. Detect and handle duplicates
7. Create unified combined dataset
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import re
from difflib import get_close_matches
import streamlit as st

import utils
import config


class DataProcessor:
    """Enhanced data processor for transaction files."""
    
    def __init__(self):
        self.mapping_file = os.path.join("data", "processed", "transaction_mappings.json")
        self.combined_file = os.path.join("data", "processed", "transactions_combined_enhanced.csv")
        self.mappings = self._load_mappings()
        
    def _load_mappings(self) -> Dict:
        """Load transaction mappings from JSON file."""
        if os.path.exists(self.mapping_file):
            try:
                with open(self.mapping_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                st.warning(f"Error loading mappings: {e}")
                return self._create_default_mappings()
        else:
            return self._create_default_mappings()
    
    def _create_default_mappings(self) -> Dict:
        """Create default mapping structure."""
        default_mappings = {
            "mappings": {},
            "lists": {
                "account_types": ["income", "expense", "transfer"],
                "categories": ["Food & Dining", "Transportation", "Entertainment", "Utilities", "Healthcare", "Shopping"],
                "tags": ["essential", "luxury", "monthly", "annual", "subscription"],
                "payers": ["Self", "Employer", "Bank", "Investment"],
                "payees": ["Grocery Store", "Gas Station", "Restaurant", "Utility Company"]
            }
        }
        self._save_mappings(default_mappings)
        return default_mappings
    
    def _save_mappings(self, mappings: Dict) -> None:
        """Save mappings to JSON file."""
        os.makedirs(os.path.dirname(self.mapping_file), exist_ok=True)
        with open(self.mapping_file, 'w', encoding='utf-8') as f:
            json.dump(mappings, f, indent=2, ensure_ascii=False)
    
    def _extract_filename_metadata(self, filename: str) -> Tuple[str, str, str]:
        """Extract bank name, account type, and last 4 digits from filename."""
        # Pattern: transaction-raw-import-[bank]_[type]_[last4]-YYYY.MM.DD-YYYY.MM.DD.csv
        pattern = r'transaction-raw-import-([^_]+)_([^_]+)_(\d{4})-\d{4}\.\d{2}\.\d{2}-\d{4}\.\d{2}\.\d{2}'
        match = re.search(pattern, filename)
        
        if match:
            bank = match.group(1).upper()
            account_type = match.group(2).upper()
            last4 = match.group(3)
            return bank, account_type, last4
        else:
            return "UNKNOWN", "UNKNOWN", "0000"
    
    def _add_period_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add formatted period columns to DataFrame."""
        df = df.copy()
        
        # Ensure Date column is datetime
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Add period columns
        df['PeriodYear'] = df['Date'].dt.strftime('%Y')
        df['PeriodMonth'] = df['Date'].dt.strftime('%m-%Y')
        df['PeriodQuarter'] = df['Date'].dt.apply(
            lambda x: f"Q{(x.month-1)//3 + 1}-{x.year}" if pd.notnull(x) else None
        )
        
        return df
    
    def _find_best_match(self, description: str, existing_mappings: List[str]) -> Optional[str]:
        """Find the best matching description from existing mappings."""
        if not existing_mappings:
            return None
        
        # Try exact match first
        if description in existing_mappings:
            return description
        
        # Try partial matches (case insensitive)
        description_lower = description.lower()
        for mapping in existing_mappings:
            if description_lower in mapping.lower() or mapping.lower() in description_lower:
                return mapping
        
        # Try fuzzy matching
        matches = get_close_matches(description, existing_mappings, n=1, cutoff=0.6)
        return matches[0] if matches else None
    
    def _apply_mappings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply mappings to DataFrame."""
        df = df.copy()
        
        # Initialize new columns
        df['AccountType'] = None
        df['Category1'] = None
        df['Category2'] = None
        df['Category3'] = None
        df['Tags'] = None
        df['Payer'] = None
        df['Payee'] = None
        df['MappedDescription'] = None
        
        # Get existing mapping keys
        existing_descriptions = list(self.mappings.get('mappings', {}).keys())
        
        for idx, row in df.iterrows():
            description = str(row['Description']).strip()
            
            # Find best match
            best_match = self._find_best_match(description, existing_descriptions)
            
            if best_match:
                mapping = self.mappings['mappings'][best_match]
                df.at[idx, 'AccountType'] = mapping.get('account_type')
                df.at[idx, 'Category1'] = mapping.get('category1')
                df.at[idx, 'Category2'] = mapping.get('category2')
                df.at[idx, 'Category3'] = mapping.get('category3')
                df.at[idx, 'Tags'] = mapping.get('tags')
                df.at[idx, 'Payer'] = mapping.get('payer')
                df.at[idx, 'Payee'] = mapping.get('payee')
                df.at[idx, 'MappedDescription'] = best_match
        
        return df
    
    def _detect_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect and mark duplicate transactions."""
        df = df.copy()
        
        # Create a composite key for duplicate detection
        df['DuplicateKey'] = df.apply(
            lambda row: f"{row['Date']}_{row['Amount']}_{row['Description']}_{row['Bank']}_{row['AccountLast4']}", 
            axis=1
        )
        
        # Mark duplicates (keep first occurrence)
        df['IsDuplicate'] = df.duplicated(subset=['DuplicateKey'], keep='first')
        
        # Remove duplicate key column
        df = df.drop('DuplicateKey', axis=1)
        
        return df
    
    def process_all_files(self) -> pd.DataFrame:
        """Process all raw transaction files and create unified dataset."""
        # Load all transactions using existing utils
        df = utils.load_all_transactions()
        
        if df.empty:
            st.warning("No transaction files found in data/raw/ directory")
            return pd.DataFrame()
        
        # Add filename metadata
        df['Bank'] = df['FileName'].apply(lambda x: self._extract_filename_metadata(x)[0])
        df['AccountType'] = df['FileName'].apply(lambda x: self._extract_filename_metadata(x)[1])
        df['AccountLast4'] = df['FileName'].apply(lambda x: self._extract_filename_metadata(x)[2])
        
        # Create bank account identifier
        df['BankAccount'] = df['Bank'] + ' ' + df['AccountType'] + ' ' + df['AccountLast4']
        
        # Add period columns
        df = self._add_period_columns(df)
        
        # Apply mappings
        df = self._apply_mappings(df)
        
        # Detect duplicates
        df = self._detect_duplicates(df)
        
        # Add transaction type based on amount
        df['TransactionType'] = np.where(df['Amount'] >= 0, 'Incoming', 'Outgoing')
        
        # Sort by date
        df = df.sort_values('Date', ascending=False)
        
        # Save combined file
        os.makedirs(os.path.dirname(self.combined_file), exist_ok=True)
        df.to_csv(self.combined_file, index=False)
        
        # Log processing results
        total_transactions = len(df)
        mapped_transactions = len(df[df['MappedDescription'].notna()])
        duplicate_transactions = len(df[df['IsDuplicate'] == True])
        
        st.success(f"""
        ✅ Data processing complete!
        - Total transactions: {total_transactions:,}
        - Mapped transactions: {mapped_transactions:,} ({(mapped_transactions/total_transactions*100):.1f}%)
        - Duplicate transactions: {duplicate_transactions:,}
        - Combined file saved: {self.combined_file}
        """)
        
        return df
    
    def get_unmapped_transactions(self) -> pd.DataFrame:
        """Get transactions that haven't been mapped yet."""
        df = self.process_all_files()
        if df.empty:
            return pd.DataFrame()
        
        # Get unmapped transactions
        unmapped = df[df['MappedDescription'].isna()].copy()
        
        # Group by description and count occurrences
        unmapped_summary = unmapped.groupby('Description').agg({
            'Amount': ['count', 'sum'],
            'Date': ['min', 'max'],
            'BankAccount': 'first'
        }).reset_index()
        
        # Flatten column names
        unmapped_summary.columns = [
            'Description', 'TransactionCount', 'TotalAmount', 
            'FirstDate', 'LastDate', 'BankAccount'
        ]
        
        # Sort by transaction count (most frequent first)
        unmapped_summary = unmapped_summary.sort_values('TransactionCount', ascending=False)
        
        return unmapped_summary
    
    def update_mapping(self, description: str, mapping_data: Dict) -> None:
        """Update mapping for a specific description."""
        self.mappings['mappings'][description] = mapping_data
        self._save_mappings(self.mappings)
        
        # Reprocess data to apply new mapping
        self.process_all_files()
    
    def get_mapping_lists(self) -> Dict:
        """Get available options for mapping dropdowns."""
        return self.mappings.get('lists', {})
    
    def update_mapping_lists(self, list_name: str, new_items: List[str]) -> None:
        """Update available options for mapping dropdowns."""
        if 'lists' not in self.mappings:
            self.mappings['lists'] = {}
        
        self.mappings['lists'][list_name] = list(set(new_items))  # Remove duplicates
        self._save_mappings(self.mappings)


# Global instance
data_processor = DataProcessor()
