from __future__ import annotations
import pandas as pd
import folium
from typing import Dict, Hashable, List, Tuple

# === Verbatim-extracted helper logic from the user's original code ===

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
