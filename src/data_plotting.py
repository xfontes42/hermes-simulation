from typing import List, Dict

from ipdb import set_trace

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd


def plot_accumulated_actor_graph(actors_flow_acc: List[List[float]], n_runs):
    """Plot the road network occupation during the simulation"""
    # Your x and y axis
    data = np.array(actors_flow_acc)
    x, y, z = data[:, 0], data[:, 1], data[:, 2]
    y = [y/n_runs, z/n_runs]

    # use a known color palette (see..)
    pal = sns.color_palette("Set1")
    plt.stackplot(x, y, labels=['with atis', 'without atis'],
                  colors=pal, alpha=0.4)
    plt.xlabel("hours")
    plt.ylabel("actors in graph")
    plt.legend(loc='upper right')
    plt.xlim(right=30)
    plt.show()


def plot_accumulated_edges_graphs(edges_accumulated: Dict[str, List[List[float]]], n_runs):
    """Plot the actors occupation of all edges during the simulation"""
    fig = plt.figure()
    n_edges = len(edges_accumulated.keys())
    edge_list = sorted(list(edges_accumulated.keys()))
    for i, e_key in enumerate(edge_list):
        edge_data = edges_accumulated[e_key]
        edge_data = np.array(edge_data)
        x, y, z = edge_data[:, 0], edge_data[:, 1], edge_data[:, 2]
        y = [y / n_runs, z / n_runs]

        ax = fig.add_subplot(
            4,
            int((n_edges / 4 + 0.5)),
            i + 1
        )
        ax.text(.2, .9, str(e_key),
                horizontalalignment='right',
                transform=ax.transAxes)

        pal = sns.color_palette("Set1")
        ax.stackplot(x, y, labels=['atis', 'natis'], colors=pal, alpha=0.4)
        ax.legend(loc='upper right')
        plt.xlim(right=28)

    plt.show()
