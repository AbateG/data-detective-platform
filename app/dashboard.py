import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

def generate_mock_metrics():
    """Generate mock metrics for dashboard."""
    return {
        'total_datasets': np.random.randint(10, 50),
        'anomalies_detected': np.random.randint(5, 100),
        'api_calls': np.random.randint(100, 1000),
        'data_quality_score': np.random.uniform(85, 98),
        'cloud_cost': np.random.uniform(50, 200)
    }

def generate_recent_activity():
    """Generate recent activity log."""
    activities = [
        "Anomaly detected in user data",
        "API endpoint tested successfully",
        "Data flow mapped with 2 glitches found",
        "Sanity check completed on customer dataset",
        "Challenge level 3 completed",
        "Cloud data sync initiated"
    ]
    timestamps = [datetime.now() - timedelta(minutes=i*15) for i in range(len(activities))]
    return pd.DataFrame({
        'activity': activities,
        'timestamp': timestamps
    })

def check_alerts():
    """Check for system alerts."""
    alerts = []
    
    # Mock alert conditions
    if np.random.random() > 0.7:
        alerts.append({"type": "warning", "message": "High API error rate detected"})
    
    if np.random.random() > 0.8:
        alerts.append({"type": "error", "message": "Data pipeline failure in ETL process"})
    
    if np.random.random() > 0.6:
        alerts.append({"type": "info", "message": "New dataset uploaded to cloud storage"})
    
    return alerts

def generate_ai_insights():
    """Generate AI-powered insights."""
    insights = [
        "📈 Data quality has improved by 15% this week",
        "🔍 Most common anomaly type: statistical outliers in transaction amounts",
        "⚡ API response times are 20% faster than last month",
        "🎯 Challenge completion rate: 78% for medium difficulty",
        "☁️ Cloud storage costs optimized by 12%"
    ]
    return insights

def main():
    st.title("🧠 Advanced Data Detective Platform")
    st.markdown("Welcome to the ultimate data debugging and analysis tool with AI-powered insights!")

    # Sidebar navigation
    page = st.sidebar.selectbox("Choose a module", [
        "Dashboard", 
        "Data Flow Mapper", 
        "Sanity Checker", 
        "API & Log Explorer", 
        "Anomaly Detection", 
        "Challenge Mode",
        "Cloud Integration"
    ])

    # Dashboard overview
    if page == "Dashboard":
        st.header("📊 Dashboard Overview")
        
        # Key metrics
        metrics = generate_mock_metrics()
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Datasets", metrics['total_datasets'])
        
        with col2:
            st.metric("Anomalies", metrics['anomalies_detected'])
        
        with col3:
            st.metric("API Calls", metrics['api_calls'])
        
        with col4:
            st.metric("Quality Score", f"{metrics['data_quality_score']:.1f}%")
        
        with col5:
            st.metric("Cloud Cost", f"${metrics['cloud_cost']:.2f}")
        
        # Alerts section
        st.subheader("🚨 System Alerts")
        alerts = check_alerts()
        if alerts:
            for alert in alerts:
                if alert['type'] == 'error':
                    st.error(f"❌ {alert['message']}")
                elif alert['type'] == 'warning':
                    st.warning(f"⚠️ {alert['message']}")
                else:
                    st.info(f"ℹ️ {alert['message']}")
        else:
            st.success("✅ All systems operational")
        
        # AI Insights
        st.subheader("🤖 AI Insights")
        insights = generate_ai_insights()
        for insight in insights:
            st.write(insight)
        
        # Recent Activity
        st.subheader("📝 Recent Activity")
        activity_df = generate_recent_activity()
        st.dataframe(activity_df.style.format({"timestamp": lambda x: x.strftime("%H:%M")}))
        
        # Module status
        st.subheader("🔧 Module Status")
        status_data = pd.DataFrame({
            'Module': ['Data Flow Mapper', 'Sanity Checker', 'API & Log Explorer', 
                      'Anomaly Detection', 'Challenge Mode', 'Cloud Integration'],
            'Status': ['✅ Active', '✅ Active', '✅ Active', '✅ Active', '✅ Active', '✅ Active'],
            'Last Used': [datetime.now() - timedelta(hours=i) for i in range(6)]
        })
        st.dataframe(status_data.style.format({"Last Used": lambda x: x.strftime("%H:%M")}))
        
        # Data sharing status
        st.subheader("🔄 Data Sharing Status")
        shared_data = []
        if 'shared_data' in st.session_state:
            shared_data.append("Sanity Checker → Anomaly Detection")
        if 'log_data' in st.session_state:
            shared_data.append("API Explorer → Sanity Checker")
        if 'anomaly_nodes' in st.session_state:
            shared_data.append("Anomaly Detection → Data Flow Mapper")
        if 'cloud_data' in st.session_state:
            shared_data.append("Cloud Integration → Sanity Checker")
        
        if shared_data:
            for item in shared_data:
                st.success(f"✅ {item}")
        else:
            st.info("No data sharing active. Use modules to share data between them.")
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔍 Run Quick Sanity Check"):
                st.info("Quick sanity check would run here...")
        
        with col2:
            if st.button("📊 Generate Report"):
                st.info("Report generation would start here...")
        
        with col3:
            if st.button("🎮 Start Challenge"):
                st.info("Challenge mode would launch here...")

    elif page == "Data Flow Mapper":
        from app.data_flow_mapper import run_data_flow_mapper
        run_data_flow_mapper()

    elif page == "Sanity Checker":
        from app.sanity_checker import run_sanity_checker
        run_sanity_checker()

    elif page == "API & Log Explorer":
        from app.api_log_explorer import run_api_log_explorer
        run_api_log_explorer()

    elif page == "Anomaly Detection":
        from app.anomaly_detection import run_anomaly_detection
        run_anomaly_detection()

    elif page == "Challenge Mode":
        from app.challenge_mode import run_challenge_mode
        run_challenge_mode()

    elif page == "Cloud Integration":
        from app.cloud_integration import run_cloud_integration
        run_cloud_integration()

if __name__ == "__main__":
    main()
