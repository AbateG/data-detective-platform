import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

def detect_anomalies(df, algorithm='Isolation Forest', contamination=0.1, **kwargs):
    """Detect anomalies using specified algorithm."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) == 0:
        return None, "No numeric columns found for anomaly detection"
    
    X = df[numeric_cols].values
    
    # Scale the data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    if algorithm == 'Isolation Forest':
        model = IsolationForest(contamination=contamination, random_state=42, **kwargs)
        predictions = model.predict(X_scaled)
        scores = model.decision_function(X_scaled)
    
    elif algorithm == 'One-Class SVM':
        model = OneClassSVM(nu=contamination, **kwargs)
        predictions = model.predict(X_scaled)
        scores = model.decision_function(X_scaled)
    
    elif algorithm == 'Local Outlier Factor':
        model = LocalOutlierFactor(contamination=contamination, **kwargs)
        predictions = model.fit_predict(X_scaled)
        scores = model.negative_outlier_factor_
    
    # Convert predictions: -1 for anomaly, 1 for normal
    anomalies = (predictions == -1)
    
    return {
        'predictions': predictions,
        'anomalies': anomalies,
        'scores': scores,
        'model': model,
        'scaler': scaler,
        'numeric_cols': numeric_cols
    }, None

def explain_anomalies(df, result):
    """Provide explanations for detected anomalies."""
    anomalies_df = df[result['anomalies']].copy()
    normal_df = df[~result['anomalies']].copy()
    
    explanations = []
    
    for col in result['numeric_cols']:
        anomaly_mean = anomalies_df[col].mean()
        normal_mean = normal_df[col].mean()
        diff = abs(anomaly_mean - normal_mean)
        
        if diff > normal_df[col].std():
            direction = "higher" if anomaly_mean > normal_mean else "lower"
            explanations.append(f"{col}: Anomalies have {direction} values (diff: {diff:.2f})")
    
    return explanations

def detect_time_series_anomalies(df, time_col, value_col, window=10, threshold=2):
    """Detect anomalies in time series data."""
    if time_col not in df.columns or value_col not in df.columns:
        return None, "Time or value column not found"
    
    df_ts = df.copy()
    df_ts[time_col] = pd.to_datetime(df_ts[time_col])
    df_ts = df_ts.sort_values(time_col)
    
    # Rolling statistics
    df_ts['rolling_mean'] = df_ts[value_col].rolling(window=window).mean()
    df_ts['rolling_std'] = df_ts[value_col].rolling(window=window).std()
    
    # Z-score based anomaly detection
    df_ts['z_score'] = (df_ts[value_col] - df_ts['rolling_mean']) / df_ts['rolling_std']
    anomalies = abs(df_ts['z_score']) > threshold
    
    return {
        'anomalies': anomalies,
        'z_scores': df_ts['z_score'],
        'rolling_mean': df_ts['rolling_mean'],
        'rolling_std': df_ts['rolling_std']
    }, None

def run_anomaly_detection():
    st.header("🚨 Advanced Anomaly Detection")
    st.write("Multi-algorithm anomaly detection with explainability and time-series support.")
    
    # Data source
    data_source = st.radio("Data Source:", ["Upload File", "Use Shared Data", "Generate Sample"])
    
    df = None
    
    if data_source == "Upload File":
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
    
    elif data_source == "Use Shared Data":
        if st.session_state.get('shared_data') is not None:
            df = st.session_state['shared_data']
            st.success("Using data from Sanity Checker!")
        else:
            st.warning("No shared data available. Please use Sanity Checker first.")
    
    elif data_source == "Generate Sample":
        if st.button("Generate Sample Data"):
            np.random.seed(42)
            n_samples = 1000
            normal_data = np.random.normal(0, 1, (n_samples, 2))
            # Add some anomalies
            anomalies = np.random.uniform(-5, 5, (int(n_samples * 0.05), 2))
            data = np.vstack([normal_data, anomalies])
            df = pd.DataFrame(data, columns=['feature1', 'feature2'])
            st.success("Sample data generated!")
    
    if df is not None:
        st.subheader("Data Preview")
        st.dataframe(df.head())
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", len(df))
        with col2:
            st.metric("Columns", len(df.columns))
        with col3:
            numeric_cols = len(df.select_dtypes(include=[np.number]).columns)
            st.metric("Numeric Columns", numeric_cols)
        
        # Algorithm selection
        st.subheader("Anomaly Detection Settings")
        col1, col2 = st.columns(2)
        
        with col1:
            algorithm = st.selectbox("Algorithm:", 
                                   ["Isolation Forest", "One-Class SVM", "Local Outlier Factor"])
        
        with col2:
            contamination = st.slider("Contamination (%):", 1, 20, 10) / 100
        
        # Advanced options
        with st.expander("Advanced Parameters"):
            if algorithm == "Isolation Forest":
                n_estimators = st.slider("Number of Estimators:", 50, 200, 100)
                max_features = st.slider("Max Features:", 0.5, 1.0, 1.0)
                kwargs = {'n_estimators': n_estimators, 'max_features': max_features}
            elif algorithm == "One-Class SVM":
                kernel = st.selectbox("Kernel:", ["rbf", "linear", "poly", "sigmoid"])
                gamma = st.selectbox("Gamma:", ["scale", "auto"], index=0)
                kwargs = {'kernel': kernel, 'gamma': gamma}
            else:  # Local Outlier Factor
                n_neighbors = st.slider("Number of Neighbors:", 5, 50, 20)
                kwargs = {'n_neighbors': n_neighbors}
        
        # Time series option
        is_time_series = st.checkbox("Time Series Data")
        if is_time_series:
            time_col = st.selectbox("Time Column:", df.columns)
            value_col = st.selectbox("Value Column:", df.select_dtypes(include=[np.number]).columns)
        
        if st.button("Detect Anomalies"):
            with st.spinner("Running anomaly detection..."):
                if is_time_series:
                    result, error = detect_time_series_anomalies(df, time_col, value_col)
                    if error:
                        st.error(error)
                    else:
                        anomalies_count = result['anomalies'].sum()
                        st.metric("Anomalies Detected", anomalies_count)
                        
                        # Visualization
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=df[time_col], y=df[value_col], 
                                               mode='lines', name='Original'))
                        fig.add_trace(go.Scatter(x=df[time_col][result['anomalies']], 
                                               y=df[value_col][result['anomalies']], 
                                               mode='markers', name='Anomalies',
                                               marker=dict(color='red', size=8)))
                        st.plotly_chart(fig)
                        
                        # Show anomalous data
                        st.subheader("Anomalous Data Points")
                        st.dataframe(df[result['anomalies']])
                
                else:
                    result, error = detect_anomalies(df, algorithm, contamination, **kwargs)
                    if error:
                        st.error(error)
                    else:
                        anomalies_count = result['anomalies'].sum()
                        st.metric("Anomalies Detected", anomalies_count)
                        
                        # Explanations
                        explanations = explain_anomalies(df, result)
                        if explanations:
                            st.subheader("Anomaly Explanations")
                            for exp in explanations:
                                st.write(f"• {exp}")
                        
                        # Visualization (2D scatter for first two numeric columns)
                        if len(result['numeric_cols']) >= 2:
                            fig = px.scatter(df, x=result['numeric_cols'][0], y=result['numeric_cols'][1],
                                           color=result['anomalies'].astype(str),
                                           color_discrete_map={'True': 'red', 'False': 'blue'},
                                           title="Anomaly Detection Results")
                            st.plotly_chart(fig)
                        
                        # Show anomalous data
                        st.subheader("Anomalous Records")
                        anomalous_df = df[result['anomalies']].copy()
                        anomalous_df['anomaly_score'] = result['scores'][result['anomalies']]
                        st.dataframe(anomalous_df)
                        
                        # Export results
                        csv_data = anomalous_df.to_csv(index=False)
                        st.download_button(
                            label="Download Anomalies CSV",
                            data=csv_data,
                            file_name="anomalies.csv",
                            mime="text/csv"
                        )
        
        # Integration with other modules
        if st.button("Send Anomalies to Data Flow Mapper"):
            if 'result' in locals() and result:
                anomaly_nodes = [f"Anomaly_{i}" for i in range(result['anomalies'].sum())]
                st.session_state['anomaly_nodes'] = anomaly_nodes
                st.success("Anomaly data sent to Data Flow Mapper!")
            else:
                st.warning("No anomaly results available to send.")
