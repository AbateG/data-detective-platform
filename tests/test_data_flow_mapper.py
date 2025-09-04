import pytest
import networkx as nx
import pandas as pd
from app.data_flow_mapper import parse_sql_to_graph, detect_glitches

def test_parse_sql_to_graph():
    """Test SQL query parsing to data flow graph."""
    sql = "SELECT * FROM users JOIN orders ON users.id = orders.user_id"
    G = parse_sql_to_graph(sql)
    
    assert isinstance(G, nx.DiGraph)
    assert len(G.nodes()) > 0
    assert len(G.edges()) > 0

def test_detect_glitches():
    """Test glitch detection in data flow graphs."""
    # Create a graph with a cycle
    G = nx.DiGraph()
    G.add_edges_from([('A', 'B'), ('B', 'C'), ('C', 'A')])
    
    glitches = detect_glitches(G)
    
    assert len(glitches) > 0
    assert any('cycle' in glitch.lower() for glitch in glitches)

def test_detect_glitches_no_issues():
    """Test glitch detection on a clean graph."""
    G = nx.DiGraph()
    G.add_edges_from([('A', 'B'), ('B', 'C'), ('C', 'D')])
    
    glitches = detect_glitches(G)
    
    # Should not detect cycles or isolated nodes
    assert not any('cycle' in glitch.lower() for glitch in glitches)
    assert not any('isolated' in glitch.lower() for glitch in glitches)

def test_graph_with_isolated_nodes():
    """Test detection of isolated nodes."""
    G = nx.DiGraph()
    G.add_edges_from([('A', 'B'), ('B', 'C')])
    G.add_node('D')  # Isolated node
    
    glitches = detect_glitches(G)
    
    assert any('isolated' in glitch.lower() for glitch in glitches)
