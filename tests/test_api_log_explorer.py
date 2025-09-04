import pytest
import pandas as pd
from app.api_log_explorer import parse_log_line, detect_log_anomalies

def test_parse_log_line():
    """Test parsing of individual log lines."""
    log_line = "2023-09-01 10:15:23 INFO User login successful"
    
    parsed = parse_log_line(log_line)
    
    assert parsed['timestamp'] == "2023-09-01 10:15:23"
    assert parsed['level'] == "INFO"
    assert 'login' in parsed['raw']

def test_parse_log_line_no_match():
    """Test parsing of log line with no standard format."""
    log_line = "This is not a standard log line"
    
    parsed = parse_log_line(log_line)
    
    assert parsed['raw'] == log_line
    assert parsed.get('level') is None

def test_detect_log_anomalies_high_error_rate():
    """Test detection of high error rate in logs."""
    data = {
        'level': ['INFO'] * 85 + ['ERROR'] * 15,  # 15% error rate
        'timestamp': ['2023-09-01 10:00:00'] * 100,
        'status_code': [200] * 100
    }
    logs_df = pd.DataFrame(data)
    
    anomalies = detect_log_anomalies(logs_df)
    
    assert len(anomalies) > 0
    assert any('error rate' in anomaly.lower() for anomaly in anomalies)

def test_detect_log_anomalies_unusual_status():
    """Test detection of unusual HTTP status codes."""
    data = {
        'level': ['INFO'] * 95 + ['ERROR'] * 5,
        'timestamp': ['2023-09-01 10:00:00'] * 100,
        'status_code': [200] * 90 + [500] * 10  # Unusual 500 errors
    }
    logs_df = pd.DataFrame(data)
    
    anomalies = detect_log_anomalies(logs_df)
    
    assert len(anomalies) > 0
    assert any('status' in anomaly.lower() for anomaly in anomalies)

def test_detect_log_anomalies_no_anomalies():
    """Test log analysis with no anomalies."""
    data = {
        'level': ['INFO'] * 95 + ['WARNING'] * 5,
        'timestamp': ['2023-09-01 10:00:00'] * 100,
        'status_code': [200] * 100
    }
    logs_df = pd.DataFrame(data)
    
    anomalies = detect_log_anomalies(logs_df)
    
    # Should not detect high error rate or unusual status codes
    assert not any('error rate' in anomaly.lower() for anomaly in anomalies)
    assert not any('status' in anomaly.lower() for anomaly in anomalies)
