from __future__ import annotations
import heapq
from typing import Dict, Hashable, List, Tuple

# Graph type alias aligned with original structure (adjacency list with costs)
Graph = Dict[Hashable, List[Tuple[Hashable, float]]]

# === Verbatim from user's original code ===

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
