import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime

# Challenge data
CHALLENGES = {
    1: {
        "title": "Basic Anomaly Hunt",
        "description": "Find the obvious outlier in this simple dataset.",
        "difficulty": "Easy",
        "points": 10,
        "type": "anomaly",
        "data": lambda: generate_anomaly_data(100, 1),
        "answer": "Index 50 has an extreme value"
    },
    2: {
        "title": "Data Cleaning Challenge",
        "description": "Identify and fix data quality issues in this messy dataset.",
        "difficulty": "Medium",
        "points": 20,
        "type": "cleaning",
        "data": lambda: generate_messy_data(),
        "answer": "Remove duplicates, fix negative ages, handle missing values"
    },
    3: {
        "title": "SQL Mystery",
        "description": "Write a SQL query to find suspicious transactions.",
        "difficulty": "Hard",
        "points": 30,
        "type": "sql",
        "data": lambda: generate_transaction_data(),
        "answer": "SELECT * FROM transactions WHERE amount > 10000 OR amount < 0"
    },
    4: {
        "title": "Time Series Anomaly",
        "description": "Detect anomalies in this time series data.",
        "difficulty": "Medium",
        "points": 25,
        "type": "timeseries",
        "data": lambda: generate_time_series_anomaly(),
        "answer": "Anomalies at timestamps with extreme deviations"
    },
    5: {
        "title": "Schema Detective",
        "description": "Find inconsistencies between two similar datasets.",
        "difficulty": "Hard",
        "points": 35,
        "type": "schema",
        "data": lambda: generate_schema_mismatch(),
        "answer": "Column name differences, data type mismatches, missing columns"
    }
}

def generate_anomaly_data(n, std):
    """Generate data with a clear anomaly."""
    data = np.random.normal(0, std, n)
    data[50] = 10  # obvious anomaly
    return pd.DataFrame({'value': data})

def generate_messy_data():
    """Generate messy data with various issues."""
    np.random.seed(42)
    data = {
        'name': ['Alice', 'Bob', 'Charlie', 'Alice', 'David', 'Eve'],
        'age': [25, 30, -5, 25, 35, np.nan],  # negative age, duplicate, missing
        'salary': [50000, 60000, 55000, 50000, 65000, 58000]
    }
    return pd.DataFrame(data)

def generate_transaction_data():
    """Generate transaction data with suspicious patterns."""
    np.random.seed(42)
    n = 1000
    amounts = np.random.normal(1000, 200, n)
    # Add suspicious transactions
    amounts[100] = 15000  # large amount
    amounts[200] = -500   # negative amount
    amounts[300] = 12000  # another large amount
    
    data = {
        'transaction_id': range(1, n+1),
        'amount': amounts,
        'timestamp': pd.date_range('2023-01-01', periods=n, freq='H')
    }
    return pd.DataFrame(data)

def generate_time_series_anomaly():
    """Generate time series with anomalies."""
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    values = np.sin(np.arange(100) * 0.1) + np.random.normal(0, 0.1, 100)
    # Add anomalies
    values[25] = 5
    values[75] = -3
    
    return pd.DataFrame({'date': dates, 'value': values})

def generate_schema_mismatch():
    """Generate datasets with schema differences."""
    df1 = pd.DataFrame({
        'customer_id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35]
    })
    
    df2 = pd.DataFrame({
        'customer_id': [1, 2, 3],
        'full_name': ['Alice Smith', 'Bob Johnson', 'Charlie Brown'],  # different column name
        'age': ['25', '30', '35']  # different data type
    })
    
    return {'dataset1': df1, 'dataset2': df2}

def calculate_score(time_taken, hints_used, difficulty):
    """Calculate score based on time, hints, and difficulty."""
    base_score = CHALLENGES[difficulty]['points']
    time_penalty = max(0, time_taken - 300) // 10  # penalty after 5 minutes
    hint_penalty = hints_used * 5
    return max(10, base_score - time_penalty - hint_penalty)

# Achievement system
def check_achievements():
    """Check for achievements based on progress."""
    achievements = []
    
    if st.session_state.score >= 100:
        achievements.append("Data Detective 🕵️")
    
    if len(st.session_state.completed_challenges) == len(CHALLENGES):
        achievements.append("Master Detective 🏆")
    
    if st.session_state.get('hints_used', 0) == 0:
        achievements.append("No Hints Needed 🎯")
    
    return achievements

def run_challenge_mode():
    st.header("🎮 Advanced Challenge Mode")
    st.write("Test your data detective skills with progressively harder challenges!")
    
    # Initialize session state
    if 'current_level' not in st.session_state:
        st.session_state.current_level = 1
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'completed_challenges' not in st.session_state:
        st.session_state.completed_challenges = []
    if 'leaderboard' not in st.session_state:
        st.session_state.leaderboard = []
    if 'hints_used' not in st.session_state:
        st.session_state.hints_used = 0
    if 'start_time' not in st.session_state:
        st.session_state.start_time = time.time()
    
    # Sidebar with progress
    with st.sidebar:
        st.subheader("Progress")
        st.progress(st.session_state.current_level / len(CHALLENGES))
        st.write(f"Level: {st.session_state.current_level}")
        st.write(f"Score: {st.session_state.score}")
        
        if st.button("Reset Progress"):
            st.session_state.current_level = 1
            st.session_state.score = 0
            st.session_state.completed_challenges = []
            st.rerun()
    
    # Main challenge area
    level = st.session_state.current_level
    if level > len(CHALLENGES):
        st.balloons()
        st.success("🎉 Congratulations! You've completed all challenges!")
        st.metric("Final Score", st.session_state.score)
        
        # Add to leaderboard
        player_name = st.text_input("Enter your name for the leaderboard:")
        if st.button("Submit Score") and player_name:
            st.session_state.leaderboard.append({
                'name': player_name,
                'score': st.session_state.score,
                'date': datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            st.success("Score submitted!")
        
        return
    
    challenge = CHALLENGES[level]
    
    st.subheader(f"Level {level}: {challenge['title']}")
    st.write(f"**Difficulty:** {challenge['difficulty']} | **Points:** {challenge['points']}")
    st.write(challenge['description'])
    
    # Timer
    elapsed_time = time.time() - st.session_state.start_time
    st.write(f"⏱️ Time: {int(elapsed_time // 60)}:{int(elapsed_time % 60):02d}")
    
    # Challenge content
    if challenge['type'] == 'anomaly':
        data = challenge['data']()
        st.line_chart(data)
        
        user_answer = st.text_input("Where is the anomaly? (e.g., 'Index 50')")
        
    elif challenge['type'] == 'cleaning':
        data = challenge['data']()
        st.dataframe(data)
        
        st.write("**Issues to identify:**")
        issues = st.multiselect("Select issues you found:", 
                              ["Duplicates", "Negative values", "Missing data", "Inconsistent formats"])
        
        user_answer = ", ".join(issues)
        
    elif challenge['type'] == 'sql':
        data = challenge['data']()
        st.dataframe(data.head())
        
        user_answer = st.text_area("Write your SQL query:")
        
    elif challenge['type'] == 'timeseries':
        data = challenge['data']()
        st.line_chart(data.set_index('date'))
        
        user_answer = st.text_input("Describe the anomalies:")
        
    elif challenge['type'] == 'schema':
        data = challenge['data']()
        col1, col2 = st.columns(2)
        with col1:
            st.write("Dataset 1:")
            st.dataframe(data['dataset1'])
        with col2:
            st.write("Dataset 2:")
            st.dataframe(data['dataset2'])
        
        user_answer = st.text_area("Describe the schema differences:")
    
    # Hints system
    if st.button("Get Hint"):
        st.session_state.hints_used += 1
        if level == 1:
            st.info("💡 Hint: Look for values that are much higher than the others!")
        elif level == 2:
            st.info("💡 Hint: Check for duplicate names, impossible ages, and missing values!")
        elif level == 3:
            st.info("💡 Hint: Look for transactions with unusually high or negative amounts!")
        elif level == 4:
            st.info("💡 Hint: Check the chart for points that deviate significantly from the pattern!")
        elif level == 5:
            st.info("💡 Hint: Compare column names and data types between the two datasets!")
    
    # Submit answer
    if st.button("Submit Answer"):
        # Simple answer checking (in real implementation, use more sophisticated methods)
        correct = challenge['answer'].lower() in user_answer.lower()
        
        if correct:
            points_earned = calculate_score(elapsed_time, st.session_state.hints_used, level)
            st.session_state.score += points_earned
            st.session_state.completed_challenges.append(level)
            st.session_state.current_level += 1
            st.session_state.start_time = None  # Reset timer
            st.session_state.hints_used = 0  # Reset hints for next level
            
            st.success(f"✅ Correct! You earned {points_earned} points!")
            st.balloons()
            
            if level < len(CHALLENGES):
                st.info(f"Ready for Level {level + 1}?")
        else:
            st.error("❌ Not quite right. Try again or use a hint!")
    
    # Leaderboard
    st.subheader("🏆 Leaderboard")
    if st.session_state.leaderboard:
        leaderboard_df = pd.DataFrame(st.session_state.leaderboard)
        leaderboard_df = leaderboard_df.sort_values('score', ascending=False).head(10)
        st.dataframe(leaderboard_df)
    else:
        st.write("No scores yet. Be the first!")
    
    # Show achievements
    achievements = check_achievements()
    if achievements:
        st.subheader("🏅 Achievements")
        for achievement in achievements:
            st.write(f"• {achievement}")
