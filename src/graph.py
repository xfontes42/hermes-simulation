"""
Graph representing a road network.
Graph topology should allow for dynamic run-time changes (e.g. accidents
and other phenomena that restrict or even block a given edge).
"""
from typing import List, Tuple
from utils import congestion_time_estimate

import networkx as nx


class RoadGraph:

    graph: nx.DiGraph
    nstart: int
    nend: int

    def __init__(self):
        self.hardcoded_graph_2()

    def __print_edge_volumes(self):
        """Pretty print of the edges current volumes. Useful for debug purposes"""
        print("Volumes:")
        for e in self.graph.edges:
            print("\t(%i, %i) -> %i" %
                (e[0], e[1], self.graph.edges[e[0], e[1]]['volume']))

    def add_vehicle(self, edge: (int, int)):
        """Add a vehicle to a given edge"""
        self.graph.edges[edge[0], edge[1]]['volume'] += 1

    def remove_vehicle(self, edge: (int, int)):
        """Remove a vehicle from a given edge"""
        self.graph.edges[edge[0], edge[1]]['volume'] -= 1

    def get_edge_data(self, edge: Tuple[int, int]) -> dict:
        """Get edge related data. ATIS data endpoint"""
        return self.graph.edges[edge[0], edge[1]]

    def get_possible_routes(self, src_node: int, dest_node: int):
        """Get all possible routes from the src_node to the destiny_node"""
        return list(nx.all_simple_paths(self.graph, src_node, dest_node))

    def get_all_routes(self) -> List[List[int]]:
        # results in [[0, 1, 3], [0, 2, 1, 3], [0, 2, 3]]
        return self.get_possible_routes(self.nstart, self.nend)
        # this below doesn't work bc it forces to go through all nodes
        # return nx.all_topological_sorts(self.graph)

    def get_optimal_route_travel_time(self, route: List[int]) -> float:
        """Gets the estimated optimal travel time it takes to transverse a given route"""
        edges = list(zip(route, route[1:]))

        estimates = [self.graph.edges[e[0], e[1]]['free_flow_travel_time']
                     for e in edges]

        return sum(estimates)

    def get_edge_travel_time(self, edge: Tuple[int, int], volume: int) -> float:
        """Get the time it takes to transverse the edge, considering a given volume"""
        edge_data = self.get_edge_data(edge)
        return congestion_time_estimate(edge_data['free_flow_travel_time'],
                                        edge_data['capacity'],
                                        volume)

    def get_edge_real_travel_time(self, edge: Tuple[int, int]) -> float:
        """Get the real actual time it takes to transverse the edge (congestion included)"""
        return self.get_edge_travel_time(edge, self.get_edge_data(edge)['volume'])

    def hardcoded_graph_1(self):
        """Hardcoded deliverable 2 example graph for now"""
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from(range(0, 4))
        self.nstart = 0
        self.nend = 3
        self.graph.add_edges_from(
            [(0, 1), (0, 2), (2, 1), (1, 3), (2, 3)],
            volume=0,
            free_flow_travel_time=1,
            capacity=20)

    def hardcoded_graph_2(self):
        """A different hardcoded graph, see Xavier's EcoBook"""
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from([0, 1, 2, 3, 4, 5, 6, 7, 8])
        self.nstart = 0
        self.nend = 8

        self.graph.add_edges_from(
            [(0, 1), (1, 3), (3, 6), (6, 8)],
            volume=0,
            free_flow_travel_time=0.85,
            capacity=50)    # fastest path

        self.graph.add_edges_from(
            [(0, 2), (2, 5), (5, 7), (7, 8)],
            volume=0,
            free_flow_travel_time=1.17,
            capacity=50)    # shortest path

        self.graph.add_edges_from(
            [(1, 4), (2, 4), (4, 6), (4, 7)],
            volume=0,
            free_flow_travel_time=0.92,
            capacity=50)  # other recommended path
