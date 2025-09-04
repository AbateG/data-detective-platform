import pytest
import pandas as pd
import numpy as np
from app.anomaly_detection import detect_anomalies, detect_time_series_anomalies

def test_detect_anomalies_isolation_forest():
    """Test anomaly detection with Isolation Forest."""
    np.random.seed(42)
    normal_data = np.random.normal(0, 1, (100, 2))
    anomalies = np.random.uniform(-5, 5, (10, 2))
    data = np.vstack([normal_data, anomalies])
    df = pd.DataFrame(data, columns=['feature1', 'feature2'])
    
    result, error = detect_anomalies(df, 'Isolation Forest', contamination=0.1)
    
    assert error is None
    assert 'anomalies' in result
    assert 'predictions' in result
    assert result['anomalies'].sum() > 0

def test_detect_anomalies_no_numeric():
    """Test anomaly detection with no numeric columns."""
    df = pd.DataFrame({'text': ['a', 'b', 'c']})
    
    result, error = detect_anomalies(df, 'Isolation Forest')
    
    assert result is None
    assert error is not None
    assert 'numeric' in error.lower()

def test_detect_time_series_anomalies():
    """Test time series anomaly detection."""
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    values = np.sin(np.arange(100) * 0.1) + np.random.normal(0, 0.1, 100)
    values[50] = 10  # Add anomaly
    df = pd.DataFrame({'date': dates, 'value': values})
    
    result, error = detect_time_series_anomalies(df, 'date', 'value')
    
    assert error is None
    assert 'anomalies' in result
    assert result['anomalies'].sum() > 0

def test_detect_time_series_anomalies_missing_column():
    """Test time series anomaly detection with missing column."""
    df = pd.DataFrame({'value': [1, 2, 3]})
    
    result, error = detect_time_series_anomalies(df, 'date', 'value')
    
    assert result is None
    assert error is not None
