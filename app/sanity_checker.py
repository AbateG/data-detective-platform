import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import json

def detect_duplicates(df):
    """Detect duplicate rows and columns."""
    duplicates = {}
    duplicates['duplicate_rows'] = df.duplicated().sum()
    duplicates['duplicate_columns'] = df.columns.duplicated().sum()
    return duplicates

def detect_outliers(df, method='iqr'):
    """Detect outliers using IQR or Z-score method."""
    outliers = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        if method == 'iqr':
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers[col] = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
        elif method == 'zscore':
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            outliers[col] = (z_scores > 3).sum()
    
    return outliers

def check_data_consistency(df):
    """Check for data consistency issues."""
    issues = []
    
    # Check for negative values in columns that shouldn't have them
    for col in df.select_dtypes(include=[np.number]).columns:
        if 'age' in col.lower() or 'count' in col.lower() or 'price' in col.lower():
            negatives = (df[col] < 0).sum()
            if negatives > 0:
                issues.append(f"Negative values in {col}: {negatives} rows")
    
    # Check for invalid dates
    date_cols = df.select_dtypes(include=['datetime']).columns
    for col in date_cols:
        future_dates = (df[col] > pd.Timestamp.now()).sum()
        if future_dates > 0:
            issues.append(f"Future dates in {col}: {future_dates} rows")
    
    return issues

def generate_report(df, checks):
    """Generate a comprehensive sanity check report."""
    report = {
        "dataset_info": {
            "rows": len(df),
            "columns": len(df.columns),
            "memory_usage": df.memory_usage(deep=True).sum()
        },
        "checks": checks
    }
    return report

def run_sanity_checker():
    st.header("✅ Advanced Sanity Checker")
    st.write("Comprehensive data validation with automated reporting and anomaly detection integration.")
    
    # File upload
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx", "xls"])
    
    if uploaded_file is not None:
        # Load data
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.subheader("Data Overview")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Rows", len(df))
        
        with col2:
            st.metric("Columns", len(df.columns))
        
        with col3:
            st.metric("Missing Values", df.isnull().sum().sum())
        
        st.dataframe(df.head())
        
        # Validation options
        st.subheader("Validation Checks")
        checks_to_run = st.multiselect(
            "Select checks to perform:",
            ["Basic Stats", "Duplicates", "Outliers", "Consistency", "Data Types"],
            default=["Basic Stats", "Duplicates", "Outliers"]
        )
        
        checks = {}
        
        if "Basic Stats" in checks_to_run:
            st.subheader("📊 Basic Statistics")
            st.write(df.describe())
            
            # Missing values visualization
            missing_data = df.isnull().sum()
            if missing_data.sum() > 0:
                st.bar_chart(missing_data)
            
            checks["basic_stats"] = {
                "missing_values": missing_data.to_dict(),
                "data_types": df.dtypes.to_dict()
            }
        
        if "Duplicates" in checks_to_run:
            st.subheader("🔄 Duplicate Detection")
            duplicates = detect_duplicates(df)
            st.write(f"Duplicate rows: {duplicates['duplicate_rows']}")
            st.write(f"Duplicate columns: {duplicates['duplicate_columns']}")
            
            if duplicates['duplicate_rows'] > 0:
                st.warning(f"Found {duplicates['duplicate_rows']} duplicate rows!")
            
            checks["duplicates"] = duplicates
        
        if "Outliers" in checks_to_run:
            st.subheader("📈 Outlier Detection")
            outlier_method = st.selectbox("Outlier detection method:", ["IQR", "Z-Score"])
            outliers = detect_outliers(df, outlier_method.lower())
            
            st.write("Outliers per column:")
            st.bar_chart(pd.Series(outliers))
            
            checks["outliers"] = outliers
        
        if "Consistency" in checks_to_run:
            st.subheader("🔍 Data Consistency")
            consistency_issues = check_data_consistency(df)
            
            if consistency_issues:
                for issue in consistency_issues:
                    st.error(issue)
            else:
                st.success("No consistency issues found!")
            
            checks["consistency"] = consistency_issues
        
        if "Data Types" in checks_to_run:
            st.subheader("🏷️ Data Type Analysis")
            st.write("Column data types:")
            st.dataframe(pd.DataFrame({
                'Column': df.columns,
                'Data Type': df.dtypes,
                'Unique Values': df.nunique(),
                'Null Count': df.isnull().sum()
            }))
        
        # Generate report
        if st.button("Generate Report"):
            report = generate_report(df, checks)
            st.subheader("📋 Sanity Check Report")
            st.json(report)
            
            # Download report
            report_json = json.dumps(report, indent=2)
            st.download_button(
                label="Download Report",
                data=report_json,
                file_name="sanity_check_report.json",
                mime="application/json"
            )
        
        # Integration with other modules
        st.subheader("🔗 Integration")
        if st.button("Send to Anomaly Detection"):
            st.session_state['shared_data'] = df
            st.success("Data sent to Anomaly Detection module!")
        
        if st.button("Send to Data Flow Mapper"):
            # Extract schema for flow mapping
            schema = {col: str(dtype) for col, dtype in df.dtypes.items()}
            st.session_state['schema_data'] = schema
            st.success("Schema sent to Data Flow Mapper!")

# Store shared data in session state for cross-module communication
if 'shared_data' not in st.session_state:
    st.session_state['shared_data'] = None

if 'schema_data' not in st.session_state:
    st.session_state['schema_data'] = None
