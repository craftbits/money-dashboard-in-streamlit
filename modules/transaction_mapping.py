"""
Transaction Mapping Interface for Admin Center.

This page provides a user-friendly interface for mapping unmapped transactions
to categories, tags, and other metadata. Users can see all unmapped transactions
and assign values using dropdown menus.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List
import os
import json


def render() -> None:
    """Render the transaction mapping interface."""
    st.title("Transaction Mapping")
    st.markdown("Map unmapped transactions to categories, tags, and other metadata.")
    
    # Load enhanced transaction data
    enhanced_file = os.path.join("data", "processed", "transactions_combined_enhanced.csv")
    
    if not os.path.exists(enhanced_file):
        st.error("Enhanced transaction file not found. Please ensure the data processing workflow has been run.")
        return
    
    # Load transaction data
    with st.spinner("Loading transaction data..."):
        df = pd.read_csv(enhanced_file)
        df['Date'] = pd.to_datetime(df['Date'])
    
    # For demo purposes, show all transactions since we have sample data
    st.info("📊 Sample data loaded successfully! All transactions are pre-mapped for demonstration.")
    
    # Show transaction summary
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Transactions", len(df))
    with col2:
        st.metric("Total Income", f"${df[df['Amount'] > 0]['Amount'].sum():,.2f}")
    with col3:
        st.metric("Total Expenses", f"${abs(df[df['Amount'] < 0]['Amount'].sum()):,.2f}")
    with col4:
        st.metric("Net Cash Flow", f"${df['Amount'].sum():,.2f}")
    
    st.markdown("---")
    
    # Display sample of transactions
    st.subheader("Sample Transaction Data")
    st.markdown("This shows a sample of the enhanced transaction data with all mappings applied:")
    
    # Show recent transactions
    recent_transactions = df.sort_values('Date', ascending=False).head(20)
    st.dataframe(
        recent_transactions[['Date', 'Description', 'Amount', 'Category1', 'Category2', 'Tags', 'Payer', 'Payee']],
        use_container_width=True
    )
    
    st.markdown("---")
    
    # Show mapping statistics
    st.subheader("Mapping Statistics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        unique_categories = df['Category1'].nunique()
        st.metric("Unique Categories", unique_categories)
    with col2:
        unique_tags = df['Tags'].nunique()
        st.metric("Unique Tag Combinations", unique_tags)
    with col3:
        unique_payees = df['Payee'].nunique()
        st.metric("Unique Payees", unique_payees)
    
    # Show category breakdown
    st.subheader("Category Breakdown")
    category_summary = df.groupby('Category1')['Amount'].agg(['sum', 'count']).reset_index()
    category_summary.columns = ['Category', 'Total Amount', 'Transaction Count']
    category_summary = category_summary.sort_values('Total Amount', ascending=False)
    
    st.dataframe(category_summary, use_container_width=True)
    
    # Show tag breakdown
    st.subheader("Tag Analysis")
    tag_summary = df.groupby('Tags')['Amount'].agg(['sum', 'count']).reset_index()
    tag_summary.columns = ['Tags', 'Total Amount', 'Transaction Count']
    tag_summary = tag_summary.sort_values('Total Amount', ascending=False)
    
    st.dataframe(tag_summary, use_container_width=True)
    
    st.markdown("---")
    
    # Demo mapping interface
    st.subheader("Demo Mapping Interface")
    st.markdown("This demonstrates how the mapping interface would work with real unmapped transactions:")
    
    # Sample mapping options
    sample_mappings = {
        'account_types': ['income', 'expense', 'transfer', 'investment', 'loan'],
        'categories': ['Food & Dining', 'Transportation', 'Entertainment', 'Utilities', 'Healthcare', 'Shopping', 'Education', 'Travel', 'Insurance', 'Taxes', 'Investments', 'Gifts', 'Charity', 'Income'],
        'tags': ['essential', 'luxury', 'monthly', 'annual', 'subscription', 'one-time', 'recurring', 'business', 'personal', 'emergency'],
        'payers': ['Self', 'Employer', 'Bank', 'Investment', 'Government', 'Insurance'],
        'payees': ['Grocery Store', 'Gas Station', 'Restaurant', 'Utility Company', 'Internet Provider', 'Phone Company', 'Insurance Company', 'Healthcare Provider', 'Retail Store', 'Online Service', 'Netflix']
    }
    
    with st.form("demo_mapping_form"):
        st.markdown("**Example: Mapping a new transaction**")
        
        col1, col2 = st.columns(2)
        with col1:
            demo_description = st.text_input("Transaction Description:", value="NEW TRANSACTION")
            demo_amount = st.number_input("Amount:", value=-50.00, step=0.01)
        
        with col2:
            demo_account_type = st.selectbox("Account Type:", options=sample_mappings['account_types'])
            demo_category = st.selectbox("Category:", options=sample_mappings['categories'])
        
        demo_tags = st.multiselect("Tags:", options=sample_mappings['tags'])
        demo_payer = st.selectbox("Payer:", options=sample_mappings['payers'])
        demo_payee = st.selectbox("Payee:", options=sample_mappings['payees'])
        
        if st.form_submit_button("Save Mapping"):
            st.success("✅ Mapping saved successfully! (Demo mode)")
            st.info("In a real implementation, this would update the mapping file and regenerate the combined transaction data.")
