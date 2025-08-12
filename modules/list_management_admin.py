"""
List Management Interface for Admin Center.

This page allows users to create and customize lists that are used in the
mapping system and dropdown menus throughout the application.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List
import os
import json


def render() -> None:
    """Render the list management interface."""
    st.title("List Management")
    st.markdown("Create and customize lists used in transaction mapping and dropdown menus.")
    
    # Sample mapping lists for demonstration
    mapping_lists = {
        'account_types': ['income', 'expense', 'transfer', 'investment', 'loan'],
        'categories': ['Food & Dining', 'Transportation', 'Entertainment', 'Utilities', 'Healthcare', 'Shopping', 'Education', 'Travel', 'Insurance', 'Taxes', 'Investments', 'Gifts', 'Charity', 'Income'],
        'tags': ['essential', 'luxury', 'monthly', 'annual', 'subscription', 'one-time', 'recurring', 'business', 'personal', 'emergency'],
        'payers': ['Self', 'Employer', 'Bank', 'Investment', 'Government', 'Insurance'],
        'payees': ['Grocery Store', 'Gas Station', 'Restaurant', 'Utility Company', 'Internet Provider', 'Phone Company', 'Insurance Company', 'Healthcare Provider', 'Retail Store', 'Online Service', 'Netflix']
    }
    
    st.info("📊 This is a demonstration of the list management interface using sample data.")
    
    # Display current lists
    st.subheader("Current Lists")
    
    # Create tabs for different list types
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Account Types", "Categories", "Tags", "Payers", "Payees"
    ])
    
    with tab1:
        _render_list_editor("account_types", "Account Types", mapping_lists.get('account_types', []))
    
    with tab2:
        _render_list_editor("categories", "Categories", mapping_lists.get('categories', []))
    
    with tab3:
        _render_list_editor("tags", "Tags", mapping_lists.get('tags', []))
    
    with tab4:
        _render_list_editor("payers", "Payers", mapping_lists.get('payers', []))
    
    with tab5:
        _render_list_editor("payees", "Payees", mapping_lists.get('payees', []))
    
    # Bulk operations
    st.markdown("---")
    st.subheader("Bulk Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Import Lists from CSV**")
        uploaded_file = st.file_uploader(
            "Upload CSV file with columns: list_name, item",
            type=['csv'],
            key="import_csv"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                if 'list_name' in df.columns and 'item' in df.columns:
                    st.success(f"✅ CSV loaded with {len(df)} items")
                    
                    if st.button("Import Lists"):
                        st.success("✅ Lists imported successfully! (Demo mode)")
                        st.info("In a real implementation, this would update the mapping lists and save them to the configuration file.")
                else:
                    st.error("❌ CSV must have columns: list_name, item")
            except Exception as e:
                st.error(f"❌ Error reading CSV: {e}")
    
    with col2:
        st.markdown("**Export All Lists**")
        if st.button("Export Lists to CSV"):
            # Create export DataFrame
            export_data = []
            for list_name, items in mapping_lists.items():
                for item in items:
                    export_data.append({'list_name': list_name, 'item': item})
            
            export_df = pd.DataFrame(export_data)
            csv = export_df.to_csv(index=False)
            
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="mapping_lists.csv",
                mime="text/csv"
            )
    
    # Quick add common items
    st.markdown("---")
    st.subheader("Quick Add Common Items")
    
    common_items = {
        "account_types": ["income", "expense", "transfer", "investment", "loan"],
        "categories": [
            "Food & Dining", "Transportation", "Entertainment", "Utilities", 
            "Healthcare", "Shopping", "Education", "Travel", "Insurance", 
            "Taxes", "Investments", "Gifts", "Charity"
        ],
        "tags": [
            "essential", "luxury", "monthly", "annual", "subscription", 
            "one-time", "recurring", "business", "personal", "emergency"
        ],
        "payers": ["Self", "Employer", "Bank", "Investment", "Government", "Insurance"],
        "payees": [
            "Grocery Store", "Gas Station", "Restaurant", "Utility Company",
            "Internet Provider", "Phone Company", "Insurance Company",
            "Healthcare Provider", "Retail Store", "Online Service"
        ]
    }
    
    for list_name, items in common_items.items():
        with st.expander(f"Quick Add {list_name.replace('_', ' ').title()}"):
            # Show current items
            current_items = mapping_lists.get(list_name, [])
            missing_items = [item for item in items if item not in current_items]
            
            if missing_items:
                selected_items = st.multiselect(
                    f"Select {list_name} to add:",
                    options=missing_items,
                    key=f"quick_add_{list_name}"
                )
                
                if st.button(f"Add Selected {list_name}", key=f"add_{list_name}"):
                    st.success(f"✅ Added {len(selected_items)} items to {list_name} (Demo mode)")
                    st.info("In a real implementation, this would update the mapping lists.")
            else:
                st.info(f"All common {list_name} items are already in the list.")


def _render_list_editor(list_name: str, display_name: str, current_items: List[str]) -> None:
    """Render editor for a specific list."""
    st.markdown(f"**{display_name}**")
    
    # Display current items
    if current_items:
        st.markdown("Current items:")
        for i, item in enumerate(current_items):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"• {item}")
            with col2:
                if st.button("Remove", key=f"remove_{list_name}_{i}"):
                    st.success(f"✅ Removed '{item}' from {display_name} (Demo mode)")
                    st.info("In a real implementation, this would update the mapping lists.")
    else:
        st.info(f"No {display_name.lower()} defined yet.")
    
    # Add new item
    st.markdown("---")
    st.markdown("**Add New Item**")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        new_item = st.text_input(
            f"New {display_name.lower()}:",
            key=f"new_{list_name}",
            placeholder=f"Enter new {display_name.lower()}..."
        )
    with col2:
        if st.button("Add", key=f"add_{list_name}"):
            if new_item and new_item.strip():
                st.success(f"✅ Added '{new_item}' to {display_name} (Demo mode)")
                st.info("In a real implementation, this would update the mapping lists.")
            else:
                st.warning("Please enter a valid item name.")
    
    # Bulk add
    st.markdown("**Bulk Add Items**")
    bulk_items = st.text_area(
        f"Add multiple {display_name.lower()} (one per line):",
        key=f"bulk_{list_name}",
        placeholder=f"Enter {display_name.lower()} names, one per line..."
    )
    
    if st.button(f"Add All {display_name}", key=f"bulk_add_{list_name}"):
        if bulk_items.strip():
            new_items_list = [item.strip() for item in bulk_items.split('\n') if item.strip()]
            if new_items_list:
                all_items = current_items + new_items_list
                # Remove duplicates while preserving order
                unique_items = []
                for item in all_items:
                    if item not in unique_items:
                        unique_items.append(item)
                
                st.success(f"✅ Added {len(new_items_list)} items to {display_name} (Demo mode)")
                st.info("In a real implementation, this would update the mapping lists.")
        else:
            st.warning("Please enter at least one item.")
