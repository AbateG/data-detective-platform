import pytest
import pandas as pd
import numpy as np
from app.sanity_checker import detect_duplicates, detect_outliers, check_data_consistency

def test_detect_duplicates():
    """Test duplicate detection."""
    data = {
        'name': ['Alice', 'Bob', 'Alice', 'Charlie'],
        'age': [25, 30, 25, 35]
    }
    df = pd.DataFrame(data)
    
    duplicates = detect_duplicates(df)
    
    assert duplicates['duplicate_rows'] == 1  # One duplicate row
    assert duplicates['duplicate_columns'] == 0

def test_detect_outliers_iqr():
    """Test outlier detection using IQR method."""
    data = [1, 2, 3, 4, 5, 100]  # 100 is outlier
    df = pd.DataFrame({'value': data})
    
    outliers = detect_outliers(df, 'iqr')
    
    assert 'value' in outliers
    assert outliers['value'] > 0

def test_detect_outliers_zscore():
    """Test outlier detection using Z-score method."""
    data = [1, 2, 3, 4, 5, 50]  # 50 is outlier
    df = pd.DataFrame({'value': data})
    
    outliers = detect_outliers(df, 'zscore')
    
    assert 'value' in outliers
    assert outliers['value'] > 0

def test_check_data_consistency():
    """Test data consistency checks."""
    data = {
        'age': [25, -5, 30, 35],  # Negative age
        'price': [100, 200, -50, 150]  # Negative price
    }
    df = pd.DataFrame(data)
    
    issues = check_data_consistency(df)
    
    assert len(issues) > 0
    assert any('negative' in issue.lower() for issue in issues)

def test_check_data_consistency_clean():
    """Test data consistency on clean data."""
    data = {
        'age': [25, 30, 35, 40],
        'price': [100, 200, 150, 175]
    }
    df = pd.DataFrame(data)
    
    issues = check_data_consistency(df)
    
    assert len(issues) == 0
