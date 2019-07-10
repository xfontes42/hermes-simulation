"""
Class resembling an ATIS - Advanced Traveler Information Systems.
Has knwoledge about the roadgraph characteristcs
"""
from typing import List, Tuple
from queue import PriorityQueue
from graph import RoadGraph
from abc import ABC, abstractmethod
from utils import MultimodalDistribution


class Atis(ABC):
    """Class to encapsulate the different types of ATIS implementations"""

    graph: RoadGraph
    percentage_usage: int

    def __init__(self, graph: RoadGraph, p_usage: float):
        self.percentage_usage = p_usage
        self.graph = graph

    @abstractmethod
    def get_edge_predicted_tt(self, edge: (int, int), timestamp: float):
        """Get the estimated travel time for a given edge."""
        pass

    def get_predicted_tt_from_edges(self, edges: List[Tuple[int, int]], _: float):
        """Get the estimated travel time for a given set of sequential edges"""
        return sum([self.get_edge_predicted_tt(e, _) for e in edges])

    def get_predicted_tt_from_nodes(self, route: List[int], timestamp: float):
        """Get the travel time associated to a set of sequential nodes - a route"""
        edges = list(zip(
            route, route[1:]))     # [(r[i],r[i+1]) for i in range(len(r)-1)] <- for bigger lists
        return self.get_predicted_tt_from_edges(edges, timestamp)

    def get_edge_prediction(self, src_node: int, dest_node: int, timestamp: float):
        """Get the fastest edge that takes the actor from the node 'src_node'
        to the node 'dest_node'"""
        routes = [route for route
                  in self.graph.get_possible_routes(src_node, dest_node)]

        tts = [self.get_predicted_tt_from_nodes(route, timestamp)
               for route in routes]
        idx = tts.index(min(tts))

        return tuple(routes[idx][:2])


class CurrentAtis(Atis):
    """Atis that uses the current network congestion values to make its estimates"""

    def get_edge_predicted_tt(self, edge: (int, int), _: float):
        return self.graph.get_edge_real_travel_time(edge)


class PrevisionAtis(Atis):
    """
    Atis that assumes a constant relation through time regarding
    an edge volume and the actors global distribution, and uses that
    ratio to predict the network congestion in the future arrival
    timestamps of an actor to an edge
    """

    traffic_dist: MultimodalDistribution
    num_actors: int

    def __init__(self, graph: RoadGraph, p_usage: float, td: MultimodalDistribution, num_actors: int):
        super().__init__(graph, p_usage)
        self.traffic_dist = td
        self.num_actors = num_actors

    def get_edge_predicted_tt(self, edge: (int, int), timestamp: float):
        return self.graph.get_edge_travel_time(edge, self.traffic_dist.pdf(timestamp) * self.num_actors)

    def get_predicted_tt_from_edges(self, edges: List[Tuple[int, int]], ts: float):
        timestamp = ts
        estimates = []

        for e in edges:
            # ratio = edge real travel time \
            #   edge expected travel time according to traffic distribution
            # ts = predicted timestamp * ratio
            travel_time = self.get_edge_predicted_tt(e, timestamp) *\
                (self.graph.get_edge_real_travel_time(e)
                 / self.get_edge_predicted_tt(e, ts))

            estimates.append(travel_time)
            timestamp += travel_time

        # print(estimates)
        return sum(estimates)


class AdherenceAtis(Atis):
    """
    Atis that uses the current values to make its estimates.
    By knowing how many atis users are in a edge and the
    percentage of users that use atis it extrapolates
    the edge congestion value.
    
    This is the CurrentAtis without the god-like omnipotent prediction powers :)
    This is the one we're using in the paper as "CurrentAtis".
    """

    def __init__(self, graph: RoadGraph, p_usage: float, event_queue: PriorityQueue):
        super().__init__(graph, p_usage)
        self.event_queue = event_queue

    def get_edge_predicted_tt(self, edge: (int, int), _: float):
        from event import EdgeEndEvent  # This is here because of circular dependencies

        edge_atis_users = sum(
            [1 for _, ev in self.event_queue.queue
             if isinstance(ev, EdgeEndEvent) and
                ev.actor.uses_atis() and
                ev.edge == edge]
        )

        return self.graph.get_edge_travel_time(edge, edge_atis_users / self.percentage_usage)
