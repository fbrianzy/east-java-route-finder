import pandas as pd
import folium
import heapq
import time
import tracemalloc
from streamlit_folium import st_folium
import streamlit as st

# Path to your dataset
path = './east-java-cities-dataset.xlsx'

# Load and preprocess the dataset
df = pd.read_excel(path)
df = df.dropna()
df['Latitude'] = df['Latitude'].astype(str).str.replace(',', '.')
df['Longitude'] = df['Longitude'].astype(str).str.replace(',', '.')
df['Latitude'] = pd.to_numeric(df['Latitude'])
df['Longitude'] = pd.to_numeric(df['Longitude'])

# Function to extract the graph from a DataFrame
def extract_graph(df):
    graph = {}
    for _, row in df.iterrows():
        origin = row['Origin']
        destination = row['Destination']
        distance = row['Distance']
        if origin not in graph:
            graph[origin] = []
        if destination not in graph:
            graph[destination] = []
        graph[origin].append((destination, distance))
        graph[destination].append((origin, distance))  # Assuming undirected graph
    return graph

# Dijkstra's Algorithm
def dijkstra(graph, start, goal):
    djk_distances = {node: float('inf') for node in graph}
    djk_distances[start] = 0
    djk_frontier = [(0, start)]  # Priority queue
    djk_explored = set()
    djk_path = {}
    djk_visited_edges = []

    step_counter = 1

    while djk_frontier:
        dj_current_cost, djk_current_node = heapq.heappop(djk_frontier)

        if djk_current_node == goal:
            djk_path_result = []
            while djk_current_node != start:
                djk_path_result.append(djk_current_node)
                djk_current_node = djk_path[djk_current_node]
            djk_path_result.append(start)
            djk_path_result.reverse()
            return djk_path_result, dj_current_cost, djk_visited_edges

        if djk_current_node not in djk_explored:
            djk_explored.add(djk_current_node)
            for neighbor, cost in graph.get(djk_current_node, []):
                djk_new_cost = dj_current_cost + cost
                if djk_new_cost < djk_distances[neighbor]:
                    djk_distances[neighbor] = djk_new_cost
                    heapq.heappush(djk_frontier, (djk_new_cost, neighbor))
                    djk_path[neighbor] = djk_current_node
                    djk_visited_edges.append((djk_current_node, neighbor, step_counter))
                    step_counter += 1

    return None, float('inf'), djk_visited_edges  # No path found

# UCS Algorithm
def ucs(graph, start, goal):
    ucs_frontier = []  # Priority queue
    heapq.heappush(ucs_frontier, (0, start))  # Format: (cost, node)
    ucs_explored = set()  # Set of visited nodes
    ucs_path = {}  # Track the ucs_path
    ucs_visited_edges = []

    step_counter = 1

    while ucs_frontier:
        ucs_current_cost, ucs_current_node = heapq.heappop(ucs_frontier)

        if ucs_current_node == goal:  # Goal reached
            ucs_path_result = []
            ucs_total_cost = 0

            while ucs_current_node != start:
                previous_node = ucs_path[ucs_current_node]
                for neighbor, cost in graph[previous_node]:
                    if neighbor == ucs_current_node:
                        ucs_total_cost += cost  # Add the cost of this edge
                        break
                ucs_path_result.append(ucs_current_node)
                ucs_current_node = previous_node

            ucs_path_result.append(start)
            ucs_path_result.reverse()
            return ucs_path_result, ucs_total_cost, ucs_visited_edges

        if ucs_current_node not in ucs_explored:
            ucs_explored.add(ucs_current_node)
            for neighbor, cost in graph.get(ucs_current_node, []):
                if neighbor not in ucs_explored:
                    ucs_new_cost = ucs_current_cost + cost  # Add the cost to reach the neighbor
                    heapq.heappush(ucs_frontier, (ucs_new_cost, neighbor))
                    ucs_path[neighbor] = ucs_current_node
                    ucs_visited_edges.append((ucs_current_node, neighbor, step_counter))
                    step_counter += 1

    return None, float('inf'), ucs_visited_edges  # No ucs_path found

# Measure execution time with repetitions
def measure_execution_time(func, *args, repetitions=10):
    start_time = time.perf_counter()
    for _ in range(repetitions):
        func(*args)
    total_time = time.perf_counter() - start_time
    return total_time / repetitions

# Function to visualize the graph on the map and highlight the path and visited edges
def visualize_on_map(df, path, visited_edges, city_coords):
    avg_lat = df['Latitude'].mean()
    avg_lon = df['Longitude'].mean()
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=6)

    for _, row in df.iterrows():
        origin = row['Origin']
        destination = row['Destination']
        origin_coords = city_coords[origin]
        dest_coords = city_coords[destination]

        # Default gray color for all routes
        folium.PolyLine([origin_coords, dest_coords], color='gray', weight=1.5, opacity=0.5).add_to(m)

    if visited_edges:
        # Highlight visited edges in blue and add step numbers
        for edge in visited_edges:
            origin, destination, step = edge
            origin_coords = city_coords[origin]
            dest_coords = city_coords[destination]
            folium.PolyLine([origin_coords, dest_coords], color='blue', weight=2, opacity=0.8).add_to(m)
            mid_point = [(origin_coords[0] + dest_coords[0]) / 2, (origin_coords[1] + dest_coords[1]) / 2]
            folium.Marker(mid_point, icon=folium.DivIcon(html=f'<div style="font-size: 10pt; color: blue;">{step}</div>')).add_to(m)

    if path:
        # Highlight selected path in red
        path_coords = [city_coords[city] for city in path]
        folium.PolyLine(path_coords, color='red', weight=4, opacity=0.8).add_to(m)

    for city, coords in city_coords.items():
        folium.Marker(location=coords, popup=city).add_to(m)

    return m

# Streamlit UI
def main(df):
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

main(df)
