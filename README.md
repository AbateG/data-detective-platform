# Data Detective Platform

A comprehensive data analysis and debugging platform inspired by data analyst roles, showcasing expertise in Python, SQL, cloud tools, and data visualization.

## Features

- **Dashboard**: Central hub for all tools
- **Data Flow Mapper**: Visualize data flows and identify glitches
- **Sanity Checker**: Automated validation of data pipelines
- **API & Log Explorer**: Inspect API feeds and logs for anomalies
- **Anomaly Detection**: Machine learning-based anomaly detection
- **Challenge Mode**: Gamified data mystery solving
- **Cloud Integration**: Connect to GCP, AWS, Azure data sources

## Installation

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `.\venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`

## Usage

Run the app: `streamlit run app/dashboard.py`

## Project Structure

```
data-detective-platform/
├── app/                        # Main application code
├── static/                     # Static files
├── templates/                  # HTML templates
├── tests/                      # Unit tests
├── data/                       # Sample datasets
├── notebooks/                  # Jupyter notebooks
├── scripts/                    # Utility scripts
├── README.md
├── requirements.txt
└── .gitignore
```

## Technologies

- Python
- Streamlit
- Pandas, NumPy
- Plotly, NetworkX
- Scikit-learn
- SQLAlchemy
- Cloud SDKs (GCP, AWS, Azure)
