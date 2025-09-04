import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import pandas as pd
import json
import re
from io import BytesIO

def parse_sql_to_graph(sql_query):
    """Parse a simple SQL query to extract data flow nodes and edges."""
    G = nx.DiGraph()
    
    # Extract tables and operations
    tables = re.findall(r'FROM\s+(\w+)|JOIN\s+(\w+)', sql_query, re.IGNORECASE)
    tables = [t for sub in tables for t in sub if t]
    
    operations = re.findall(r'SELECT|INSERT|UPDATE|DELETE', sql_query, re.IGNORECASE)
    
    # Add nodes
    for table in tables:
        G.add_node(table, type='table')
    for op in operations:
        G.add_node(op, type='operation')
    
    # Add edges (simplified flow)
    if tables and operations:
        G.add_edge(tables[0], operations[0])
        if len(operations) > 1:
            G.add_edge(operations[0], operations[1])
    
    return G

def detect_glitches(G):
    """Detect common glitches in data flow."""
    glitches = []
    
    # Check for cycles
    if not nx.is_directed_acyclic_graph(G):
        glitches.append("Cycle detected: Potential infinite loop in data flow")
    
    # Check for isolated nodes
    isolated = list(nx.isolates(G))
    if isolated:
        glitches.append(f"Isolated nodes: {isolated} - These may be disconnected from the flow")
    
    # Check for high degree nodes (potential bottlenecks)
    degrees = dict(G.degree())
    bottlenecks = [node for node, deg in degrees.items() if deg > 3]
    if bottlenecks:
        glitches.append(f"Potential bottlenecks: {bottlenecks} - High connectivity may indicate complexity")
    
    return glitches

def run_data_flow_mapper():
    st.header("🔍 Advanced Data Flow Mapper")
    st.write("Map, visualize, and debug data flows between systems with glitch detection and SQL integration.")
    
    # Input methods
    input_method = st.radio("Choose input method:", ["Manual Input", "SQL Query", "Upload JSON"])
    
    G = nx.DiGraph()
    
    if input_method == "Manual Input":
        st.subheader("Manual Graph Builder")
        col1, col2 = st.columns(2)
        
        with col1:
            nodes_input = st.text_area("Enter nodes (one per line):", "Source\nETL\nDatabase\nAPI")
            nodes = [n.strip() for n in nodes_input.split('\n') if n.strip()]
        
        with col2:
            edges_input = st.text_area("Enter edges (format: source->target, one per line):", "Source->ETL\nETL->Database\nDatabase->API")
            edges = []
            for line in edges_input.split('\n'):
                if '->' in line:
                    src, tgt = line.split('->')
                    edges.append((src.strip(), tgt.strip()))
        
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
    
    elif input_method == "SQL Query":
        st.subheader("SQL Query Parser")
        sql_query = st.text_area("Enter SQL query:", "SELECT * FROM users JOIN orders ON users.id = orders.user_id")
        if st.button("Parse SQL"):
            G = parse_sql_to_graph(sql_query)
            st.success("SQL parsed into data flow graph!")
    
    elif input_method == "Upload JSON":
        st.subheader("Upload Graph JSON")
        uploaded_file = st.file_uploader("Choose JSON file", type="json")
        if uploaded_file:
            data = json.load(uploaded_file)
            G = nx.node_link_graph(data)
    
    # Glitch detection
    if G.nodes:
        glitches = detect_glitches(G)
        if glitches:
            st.warning("🚨 Glitches Detected:")
            for glitch in glitches:
                st.write(f"- {glitch}")
        else:
            st.success("✅ No glitches detected in the data flow!")
    
    # Visualization
    if G.nodes:
        st.subheader("Data Flow Visualization")
        
        # Layout options
        layout = st.selectbox("Graph Layout:", ["Spring", "Circular", "Random"])
        if layout == "Spring":
            pos = nx.spring_layout(G)
        elif layout == "Circular":
            pos = nx.circular_layout(G)
        else:
            pos = nx.random_layout(G)
        
        # Create Plotly figure
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines')
        
        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        node_text = list(G.nodes())
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            hoverinfo='text',
            marker=dict(
                size=20,
                color=[deg for node, deg in G.degree()],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Connections")
            )
        )
        
        fig = go.Figure(data=[edge_trace, node_trace])
        fig.update_layout(showlegend=False, height=600)
        st.plotly_chart(fig)
        
        # Export options
        st.subheader("Export Options")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export as JSON"):
                graph_data = nx.node_link_data(G)
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(graph_data, indent=2),
                    file_name="data_flow.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("Export as PNG"):
                # Note: In a real implementation, you'd use plotly's write_image
                st.info("PNG export would require kaleido package")
    
    # Graph metrics
    if G.nodes:
        st.subheader("Graph Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Nodes", len(G.nodes()))
        
        with col2:
            st.metric("Edges", len(G.edges()))
        
        with col3:
            st.metric("Density", f"{nx.density(G):.3f}")
        
        # Additional metrics
        st.write("**Node Degrees:**")
        degrees_df = pd.DataFrame(list(G.degree()), columns=["Node", "Degree"])
        st.dataframe(degrees_df)
