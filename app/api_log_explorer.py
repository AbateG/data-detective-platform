import streamlit as st
import requests
import json
import re
import pandas as pd
from datetime import datetime
import time

def parse_log_line(line):
    """Parse a single log line into structured data."""
    # Common log patterns
    patterns = {
        'timestamp': r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
        'level': r'\b(DEBUG|INFO|WARNING|ERROR|CRITICAL)\b',
        'ip': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        'method': r'\b(GET|POST|PUT|DELETE|PATCH)\b',
        'status_code': r'\b\d{3}\b'
    }
    
    parsed = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            parsed[key] = match.group()
    
    parsed['raw'] = line
    return parsed

def detect_log_anomalies(logs_df):
    """Detect anomalies in log data."""
    anomalies = []
    
    # High error rate
    if 'level' in logs_df.columns:
        error_rate = (logs_df['level'].str.upper() == 'ERROR').mean()
        if error_rate > 0.1:  # 10% error rate
            anomalies.append(f"High error rate: {error_rate:.2%}")
    
    # Unusual status codes
    if 'status_code' in logs_df.columns:
        status_counts = logs_df['status_code'].value_counts()
        unusual_codes = status_counts[status_counts.index.astype(str).str.match(r'^[45]\d{2}$')]
        if not unusual_codes.empty:
            anomalies.append(f"Unusual status codes: {unusual_codes.to_dict()}")
    
    # Spike in requests
    if 'timestamp' in logs_df.columns:
        logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce')
        hourly_counts = logs_df.groupby(logs_df['timestamp'].dt.hour).size()
        avg_requests = hourly_counts.mean()
        spikes = hourly_counts[hourly_counts > avg_requests * 2]
        if not spikes.empty:
            anomalies.append(f"Request spikes detected at hours: {spikes.index.tolist()}")
    
    return anomalies

def test_api_endpoint(url, method='GET', headers=None, data=None, params=None):
    """Test an API endpoint and return response details."""
    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers or {},
            json=data if isinstance(data, dict) else None,
            params=params or {},
            timeout=10
        )
        
        result = {
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'headers': dict(response.headers),
            'content_type': response.headers.get('content-type', 'unknown'),
            'content_length': len(response.content)
        }
        
        # Try to parse JSON response
        try:
            result['json_response'] = response.json()
        except:
            result['text_response'] = response.text[:1000]  # Limit text
        
        return result, None
    
    except Exception as e:
        return None, str(e)

def run_api_log_explorer():
    st.header("🌐 Advanced API & Log Explorer")
    st.write("Test APIs in real-time, parse logs, detect anomalies, and monitor feeds.")
    
    tab1, tab2, tab3 = st.tabs(["API Testing", "Log Analysis", "Feed Monitor"])
    
    with tab1:
        st.subheader("🔗 API Endpoint Testing")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            url = st.text_input("API URL:", "https://jsonplaceholder.typicode.com/posts/1")
        
        with col2:
            method = st.selectbox("Method:", ["GET", "POST", "PUT", "DELETE", "PATCH"])
        
        # Advanced options
        with st.expander("Advanced Options"):
            headers_input = st.text_area("Headers (JSON):", '{"Authorization": "Bearer token"}')
            params_input = st.text_area("Query Parameters (JSON):", '{"key": "value"}')
            body_input = st.text_area("Request Body (JSON):", '{"data": "example"}')
        
        if st.button("Test API"):
            headers = json.loads(headers_input) if headers_input.strip() else None
            params = json.loads(params_input) if params_input.strip() else None
            body = json.loads(body_input) if body_input.strip() else None
            
            with st.spinner("Testing API endpoint..."):
                result, error = test_api_endpoint(url, method, headers, body, params)
            
            if error:
                st.error(f"API Test Failed: {error}")
            else:
                st.success("API Test Successful!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Status Code", result['status_code'])
                with col2:
                    st.metric("Response Time", f"{result['response_time']:.2f}s")
                with col3:
                    st.metric("Content Length", result['content_length'])
                
                # Response details
                with st.expander("Response Details"):
                    st.json(result)
                
                # Anomaly detection
                if result['status_code'] >= 400:
                    st.warning("⚠️ Error response detected!")
                
                if result['response_time'] > 5:
                    st.warning("⚠️ Slow response time detected!")
    
    with tab2:
        st.subheader("📋 Log Analysis")
        
        uploaded_file = st.file_uploader("Upload log file", type=["txt", "log", "json"])
        
        if uploaded_file is not None:
            content = uploaded_file.read().decode("utf-8")
            
            # Parse logs
            log_lines = content.split('\n')
            parsed_logs = [parse_log_line(line) for line in log_lines if line.strip()]
            
            if parsed_logs:
                logs_df = pd.DataFrame(parsed_logs)
                st.dataframe(logs_df.head(20))
                
                # Log statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Lines", len(log_lines))
                with col2:
                    if 'level' in logs_df.columns:
                        error_count = (logs_df['level'].str.upper() == 'ERROR').sum()
                        st.metric("Errors", error_count)
                with col3:
                    if 'ip' in logs_df.columns:
                        unique_ips = logs_df['ip'].nunique()
                        st.metric("Unique IPs", unique_ips)
                
                # Anomaly detection
                anomalies = detect_log_anomalies(logs_df)
                if anomalies:
                    st.warning("🚨 Anomalies Detected:")
                    for anomaly in anomalies:
                        st.write(f"- {anomaly}")
                else:
                    st.success("✅ No anomalies detected in logs!")
                
                # Visualizations
                if 'level' in logs_df.columns:
                    st.subheader("Log Level Distribution")
                    level_counts = logs_df['level'].value_counts()
                    st.bar_chart(level_counts)
                
                if 'timestamp' in logs_df.columns:
                    st.subheader("Requests Over Time")
                    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce')
                    hourly_counts = logs_df.groupby(logs_df['timestamp'].dt.hour).size()
                    st.line_chart(hourly_counts)
                
                # Integration with other modules
                if st.button("Send Log Data to Sanity Checker"):
                    st.session_state['log_data'] = logs_df
                    st.success("Log data sent to Sanity Checker!")
        st.subheader("📡 Feed Monitor")
        
        feed_url = st.text_input("Feed URL:", "https://httpbin.org/json")
        interval = st.slider("Check Interval (seconds):", 5, 60, 10)
        
        if st.button("Start Monitoring"):
            placeholder = st.empty()
            
            for i in range(10):  # Monitor for 10 intervals
                with placeholder.container():
                    st.write(f"Check #{i+1} at {datetime.now().strftime('%H:%M:%S')}")
                    
                    result, error = test_api_endpoint(feed_url)
                    
                    if error:
                        st.error(f"Feed check failed: {error}")
                    else:
                        status_color = "🟢" if result['status_code'] == 200 else "🔴"
                        st.write(f"{status_color} Status: {result['status_code']} | Response Time: {result['response_time']:.2f}s")
                        
                        if result['status_code'] != 200:
                            st.warning("Feed anomaly detected!")
                    
                    time.sleep(interval)
            
            st.success("Monitoring completed!")


