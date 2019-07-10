"""
Main project source file.
"""
from typing import List, Tuple

from actor import Actor
from data_plotting import plot_accumulated_actor_graph, plot_accumulated_edges_graphs
from simulator import Simulator
from graph import RoadGraph
from queue import PriorityQueue
from utils import softmax_travel_times, compute_average_over_time, MultimodalDistribution
from atis import PrevisionAtis, CurrentAtis, AdherenceAtis, Atis
from statistics import SimStats
from ipdb import set_trace
from pprint import pprint
from collections import defaultdict
from tqdm import trange
from functools import partial


import argparse
import numpy as np
import json
import os.path
import networkx as nx

PREVISION_ATIS = 1
REAL_ATIS = 2
ADHERENCE_ATIS = 3


def parse_args():
    parser = argparse.ArgumentParser(
        description='Systems Modelling and Simulation')

    parser.add_argument("-n", "--num_actors", default=500, type=int, metavar="N",
                        help="number of vehicles/actors to generate per simulation run")

    parser.add_argument("-r", "--runs", default=1, type=int, metavar="R", dest="n_runs",
                        help="number of times to run the simulation for")

    parser.add_argument("-thr", "--congestion_threshold", default=0.9, type=float, metavar="THRESH",
                        help="threshold when to consider a link congested, volume/capacity")

    parser.add_argument("-tmax", "--max_run_time", default=48.0, type=float, metavar="MAX_TIME",
                        dest="max_run_time", help="max time of each simulation run (in hours)")

    parser.add_argument("-atis", "--atis_percentage", default=0.0, type=float, metavar="ATIS_P",
                        help="percentage of vehicles using the ATIS system")

    parser.add_argument("-p", "--peak", type=float, nargs=2, action='append',
                        dest='traffic_peaks', metavar=("TPEAK_MEAN", "TPEAK_STD"),
                        help="mean and standard deviation of a normal distribution that represents a peak in traffic")

    parser.add_argument("-o", "--out_file", type=str, default=os.path.join("src", "results", "default.json"),
                        dest='save_path', metavar="SAVE_PATH",
                        help="place to save the result of running the simulations")

    parser.add_argument('-ap', '--atis-prevision', dest='used_atis', action='store_const',
                        const=1, help="ATIS will make use of predictions to estimate the fastest route")
    parser.add_argument('-ar', '--atis-real', dest='used_atis', action='store_const',
                        const=2, help="ATIS will make use of real times to estimate the fastest route")
    parser.add_argument('-aa', '--atis-adherence', dest='used_atis', action='store_const',
                        const=3, help="ATIS will make use of other atis users' data to estimate the fastest route")
    parser.set_defaults(used_atis=2)

    parser.add_argument("-v", "--verbose", dest='verbose', action="store_true",
                        help="allow helpful prints to be displayed")
    parser.set_defaults(verbose=False)

    parser.add_argument("-pl", "--plots", dest='plots', action="store_true",
                        help="display plots at the end of the simulation regarding the network occupation")
    parser.set_defaults(plots=True)

    return parser.parse_args()


def print_args(args):
    from pprint import PrettyPrinter
    pp = PrettyPrinter(indent=4)
    pp.pprint(vars(args))
    print()


def actor_constructor(use_atis_p: float, graph: RoadGraph, atis: Atis):
    """Calculate possible routes and give each one a probability based on how little time it takes to transverse it"""
    possible_routes = graph.get_all_routes()
    routes_times = [graph.get_optimal_route_travel_time(r)
                    for r in possible_routes]
    routes_probs = softmax_travel_times(routes_times)
    idx = np.random.choice(len(possible_routes), p=routes_probs)
    return Actor(
        possible_routes[idx],
        np.random.choice([atis, None], p=[use_atis_p, 1-use_atis_p]))


def atis_constructor(used_atis: bool, use_atis_p: float, num_actors: int, graph: RoadGraph, traffic_dist: MultimodalDistribution, events: PriorityQueue):
    # print("Created ATIS")
    switcher = {
        PREVISION_ATIS: PrevisionAtis(graph, use_atis_p, traffic_dist, num_actors),
        REAL_ATIS: CurrentAtis(graph, use_atis_p),
        ADHERENCE_ATIS: AdherenceAtis(graph, use_atis_p, events)
    }
    return switcher.get(used_atis, "Invalid Atis")


def stats_constructor(graph: RoadGraph):
    # print("Created STATS")
    return SimStats(graph)


def statistics_print(sim: Simulator):
    """Print of simulation statistics regarding ATIS and non ATIS users"""
    print()
    atis_yes, atis_no = [], []
    for a in sim.actors:
        if a.atis is not None:
            atis_yes.append(a.total_travel_time)
        else:
            atis_no.append(a.total_travel_time)

    print("ATIS YES: mean: %f || std: %f" %
          (np.mean(atis_yes), np.std(atis_yes)))
    print("ATIS NO: mean: %f || std: %f" % (np.mean(atis_no), np.std(atis_no)))


def average_all_results(all_s: List[SimStats], display_plots: bool):
    """Gather information regarding all runs and its metrics"""

    # gather summary information
    actors_wo_end = [
        len([1 for a in stats.actors if not a.reached_dest()]) for stats in all_s]
    avg_actors_not_finishing = np.sum(actors_wo_end) / len(all_s)

    actors_summary = [compute_average_over_time(
        stats.actors_in_graph) for stats in all_s]
    edges_summary = [{str(e): compute_average_over_time(stats.edges_flow_over_time[e])
                      for e in stats.edges_flow_over_time} for stats in all_s]

    # gather atis information
    atis_yes = np.hstack(
        [[a.total_travel_time for a in stats.actors if a.atis is not None] for stats in all_s])
    atis_no = np.hstack(
        [[a.total_travel_time for a in stats.actors if a.atis is None] for stats in all_s])

    results = {'avg_actors_not_finishing': avg_actors_not_finishing,
               'avg_actors': [np.mean(actors_summary), np.std(actors_summary)],
               'avg_edges': defaultdict(lambda: []),
               'time_atis_yes': [np.mean(atis_yes), np.std(atis_yes)] if len(atis_yes) > 0 else [np.nan, np.nan],
               'time_atis_no': [np.mean(atis_no), np.std(atis_no)] if len(atis_no) > 0 else [np.nan, np.nan]}

    for d in edges_summary:
        for d_k in d:
            results['avg_edges'][d_k].append(d[d_k])

    results['avg_edges'] = {
        e: [np.mean(results['avg_edges'][e]), np.std(results['avg_edges'][e])] for e in results['avg_edges']
    }

    # gather new information with atis separation
    actors_flow = [actor_tuple for s in all_s for actor_tuple in s.actors_atis]
    actors_flow = sorted(actors_flow, key=lambda t: t[0])
    actors_flow_acc = [[0.0, 0, 0]]
    for actor_tuple in actors_flow:
        actors_flow_acc.append([actor_tuple[0],
                                actor_tuple[1] + actors_flow_acc[-1][1],
                                actor_tuple[2] + actors_flow_acc[-1][2]])
    actors_flow_acc = actors_flow_acc[1:]
    results['actors_atis_natis'] = actors_flow_acc

    # the above but for every edge
    results['edges_atis_natis'] = defaultdict(lambda: [])
    for s in all_s:
        edges = s.edges_flow_atis
        for key in edges.keys():
            results['edges_atis_natis'][str(key)].append(edges[key])

    for e_key in results['edges_atis_natis'].keys():
        edge_flow = [edge_tuple for edges in results['edges_atis_natis'][e_key]
                     for edge_tuple in edges]
        edge_flow = sorted(edge_flow, key=lambda t: t[0])
        edge_flow_acc = [[0.0, 0, 0]]
        for edge_tuple in edge_flow:
            edge_flow_acc.append([edge_tuple[0],
                                  edge_tuple[1] + edge_flow_acc[-1][1],
                                  edge_tuple[2] + edge_flow_acc[-1][2]])
        edge_flow_acc = edge_flow_acc[1:]
        results['edges_atis_natis'][e_key] = edge_flow_acc

    if display_plots:
        plot_accumulated_actor_graph(actors_flow_acc, len(all_s))
        plot_accumulated_edges_graphs(results['edges_atis_natis'], len(all_s))

    return results


def main(args):
    if args.traffic_peaks is None:
        # Needed since "action=append" doesn't overwrite "default=X"
        args.traffic_peaks = [(8, 3), (18, 3)]

    print_args(args)

    sim = Simulator(config=args,
                    actor_constructor=partial(
                        actor_constructor, args.atis_percentage),
                    atis_constructor=partial(
                        atis_constructor, args.used_atis, args.atis_percentage, args.num_actors),
                    stats_constructor=stats_constructor,
                    traffic_distribution=MultimodalDistribution(*args.traffic_peaks))

    # gather stats from all runs
    all_stats = []
    for _ in trange(args.n_runs, leave=False):
        sim.run()
        sim.stats.add_actors(sim.actors)
        all_stats.append(sim.stats)

    json_object = average_all_results(all_stats, args.plots)
    json_object['graph'] = nx.readwrite.jit_data(sim.graph.graph)

    json.dump(json_object, open(args.save_path, "w+"))

    statistics_print(sim)


if __name__ == '__main__':
    main(parse_args())
