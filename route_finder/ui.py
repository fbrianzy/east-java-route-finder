from __future__ import annotations
import tracemalloc
import streamlit as st
from streamlit_folium import st_folium

from .data_loader import load_dataset
from .graph_io import extract_graph, visualize_on_map
from .utils import measure_execution_time
from .algorithms import dijkstra, ucs

# This function mirrors the original Streamlit UI logic as-is, only moved here.
def main(df=None):
    if df is None:
        df = load_dataset('./east-java-cities-dataset.xlsx')

    graph = extract_graph(df)
    city_coords = {row['Origin']: (row['Latitude'], row['Longitude']) for _, row in df.iterrows()}
    unique_cities = sorted(set(df['Origin'].unique()).union(set(df['Destination'].unique())))

    st.title("Dijkstra's vs UCS Pathfinding")

    # Sidebar
    start_city = st.sidebar.selectbox("Select Start City:", unique_cities, key="start_city")
    end_city = st.sidebar.selectbox("Select Destination City:", unique_cities, key="end_city")

    if "results" not in st.session_state:
        st.session_state.results = None

    calculate_button = st.sidebar.button("Calculate")

    if calculate_button:
        if start_city == end_city:
            st.error("Start and destination cities cannot be the same.")
        else:
            # Dijkstra's Algorithm Execution
            tracemalloc.start()
            dijkstra_time = measure_execution_time(dijkstra, graph, start_city, end_city)
            dijkstra_path, dijkstra_cost, dijkstra_visited_edges = dijkstra(graph, start_city, end_city)
            current, peak = tracemalloc.get_traced_memory()
            dijkstra_memory = peak / 1024
            tracemalloc.stop()

            # UCS Algorithm Execution
            tracemalloc.start()
            ucs_time = measure_execution_time(ucs, graph, start_city, end_city)
            ucs_path, ucs_cost, ucs_visited_edges = ucs(graph, start_city, end_city)
            current, peak = tracemalloc.get_traced_memory()
            ucs_memory = peak / 1024
            tracemalloc.stop()

            st.session_state.results = {
                "dijkstra": {
                    "path": dijkstra_path,
                    "cost": dijkstra_cost,
                    "time": dijkstra_time,
                    "memory": dijkstra_memory,
                    "visited_edges": dijkstra_visited_edges,
                },
                "ucs": {
                    "path": ucs_path,
                    "cost": ucs_cost,
                    "time": ucs_time,
                    "memory": ucs_memory,
                    "visited_edges": ucs_visited_edges,
                },
                "city_coords": city_coords,
            }

    if st.session_state.results:
        results = st.session_state.results

        # Define columns for results
        col1, col2 = st.columns(2)

        # Left column (Dijkstra)
        with col1:
            st.subheader("Dijkstra's Algorithm")
            if results["dijkstra"]["path"]:
                st.write(f"Path: {' -> '.join(results['dijkstra']['path'])}")
                st.write(f"Total Cost: {results['dijkstra']['cost']} Km")
                st.write(f"Time: {results['dijkstra']['time']:.16f} seconds")
                st.write(f"Memory Used: {results['dijkstra']['memory']:.8f} KB")
            else:
                st.write("No path found.")

            # Display Dijkstra map
            dijkstra_map = visualize_on_map(df, results["dijkstra"]["path"], results["dijkstra"]["visited_edges"], results["city_coords"])
            st_folium(dijkstra_map, width=800, height=400)

        # Right column (UCS)
        with col2:
            st.subheader("UCS Algorithm")
            if results["ucs"]["path"]:
                st.write(f"Path: {' -> '.join(results['ucs']['path'])}")
                st.write(f"Total Cost: {results['ucs']['cost']} Km")
                st.write(f"Time: {results['ucs']['time']:.16f} seconds")
                st.write(f"Memory Used: {results['ucs']['memory']:.8f} KB")
            else:
                st.write("No path found.")

            # Display UCS map
            ucs_map = visualize_on_map(df, results["ucs"]["path"], results["ucs"]["visited_edges"], results["city_coords"])
            st_folium(ucs_map, width=800, height=400)
