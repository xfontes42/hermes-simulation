"""
Events in the simulation process.
E.g. create_actor, travel_route.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Tuple

import simulator
import actor


class Event(ABC):
    """Class to encapsulate a simulation Event"""

    def __init__(self, at_time: float):
        super().__init__()
        self.at_time = at_time

    @abstractmethod
    def act(self, sim) -> List[Event]:
        pass

    def __lt__(self, other):
        return self.at_time < other.at_time

    def __eq__(self, other):
        return self.at_time == other.at_time

    def get_priorized(self) -> Tuple[float, Event]:
        return (self.at_time, self)

    def get_timestamp(self) -> float:
        return self.at_time


class CreateActorEvent(Event):
    """Event associated to the creation of an actor.
    It will trigger an edge start event for the route first edge."""

    def __init__(self, at_time: float, actor_constructor):
        super().__init__(at_time)
        self.actor_constructor = actor_constructor

    def act(self, sim: simulator.Simulator):
        a = self.actor_constructor(sim.graph, sim.atis)
        sim.actors.append(a)

        if sim.config.verbose:
            print("%f" % round(self.at_time, 5), " -- created actor %d | atis: %s" %
                  (a.actor_id, str(a.uses_atis())))

        # updating general stats only
        sim.stats.add_actor(self.at_time, a.uses_atis())
        a.start_trip(self.at_time)
        return [EdgeStartEvent(self.at_time,
                               a,
                               a.get_next_travel_edge(self.at_time))]


class EdgeStartEvent(Event):
    """
    Represents point in time in which an Actor starts travelling along an Edge.
    """

    def __init__(self, at_time: float, a: actor.Actor, edge: Tuple[int, int]):
        super().__init__(at_time)
        self.actor = a
        self.edge = edge

    def act(self, sim: simulator.Simulator):
        """
        Updates simulator's statistics (e.g. increase load/traffic on edge).
        """
        sim.stats.add_actor_edge(
            self.at_time, self.edge, self.actor.uses_atis())

        tt = sim.graph.get_edge_real_travel_time(self.edge)
        sim.graph.add_vehicle(self.edge)

        self.actor.add_time_for_edge(self.edge, tt)
        return [EdgeEndEvent(self.at_time + tt, self.actor, self.edge)]


class EdgeEndEvent(Event):
    """
    Represents point in time in which an Actor terminates travelling along an Edge.
    """

    def __init__(self, at_time: float, a: actor.Actor, edge: Tuple[int, int]):
        super().__init__(at_time)
        self.actor = a
        self.edge = edge

    def act(self, sim: simulator.Simulator):
        """
        Updates simulator's statistics (e.g. decrease load/traffic on edge),
        and creates following EdgeStartEvent (if trip is not over).
        """
        sim.stats.remove_actor_edge(
            self.at_time, self.edge, self.actor.uses_atis())

        self.actor.travel(self.at_time, self.edge)
        sim.graph.remove_vehicle(self.edge)

        if not self.actor.reached_dest():
            # Time it starts next edge its equal to the time this event ended
            return [EdgeStartEvent(self.at_time, self.actor, self.actor.get_next_travel_edge(self.at_time))]

        if sim.config.verbose:
            self.actor.print_traveled_route()

        # updating general stats
        self.actor.update_total_tt()
        sim.stats.remove_actor(self.at_time, self.actor.uses_atis())
        return []


class AccidentEvent(Event):
    """Represents an unexpected negative event on the network (e.g. traffic accidents)"""

    def __init__(self, at_time: float, edge: Tuple[int, int], scale_factor: float):
        super().__init__(at_time)
        self.edge = edge                        # edge to target
        # how much to scale target by (e.g. edge's capacity)
        self.scale_factor = scale_factor

    def act(self, sim) -> List[Event]:
        sim.graph.graph.edges[self.edge]['capacity'] *= self.scale_factor
        return []
