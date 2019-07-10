"""
File with functions/constants dedicated to configure/help the simulations.
Constants like the ones mentioned in the report and distribution functions.
"""

import math
import random
from typing import List, Tuple
from scipy.integrate import simps, trapz

import numpy as np


class MultimodalDistribution:
    """
    Class to represent a multimodal distribution: a distribution
    composed of several normal distributions with different peaks.
    """
    class UnimodalDistribution:
        def __init__(self, mean, std):
            self.mean = mean
            self.std = std

        def __call__(self):
            return np.random.normal(self.mean, self.std)

        def pdf(self, x: float) -> float:
            """Get the value of the Probability Density Function (pdf) at the given x value"""
            return 1/(np.sqrt(2 * np.pi * self.std**2)) *\
                np.exp(- (x - self.mean)**2 / (2 * self.std**2))

    def __init__(self, *dist_stats):
        self.stats = dist_stats
        self.distributions = [
            self.UnimodalDistribution(peak, std) for peak, std in self.stats
        ]

    def pdf(self, x: float) -> float:
        """Get the value of the Probability Density Function (pdf) at the given x value"""
        return sum(map(lambda dist: dist.pdf(x), self.distributions))

    def __call__(self):
        return random.choice(self.distributions)()

    @staticmethod
    def default():
        return MultimodalDistribution([8, 3], [18, 3])


def congestion_time_estimate(free_flow: float, capacity: float, volume: float) -> float:
    """US Bureau ofPublic Roads (BPR) congestion function.
    Used to compute the traverse time of an edge"""
    return free_flow * (1 + 0.15 * math.pow((volume/capacity), 4))


def softmax_travel_times(travel_times):
    """Apply the softmax function to the given array of values"""
    # invert number so that smaller travel times have higher probability
    tts = np.max(travel_times) - np.array(travel_times)
    # compute softmax values for each score in tts
    e_tt = np.exp(tts - np.max(tts))
    return e_tt / e_tt.sum(axis=0)


def compute_average_over_time(dist: List[Tuple[float, int]]):
    dist = np.array(dist)
    return trapz(dist[:, 1], dist[:, 0]) / dist[-1][0]
