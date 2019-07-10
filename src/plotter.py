import argparse
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import json
import os

from main import main as simulator

NUM_VEHICLES = [200, 400, 600, 800, 1000, 1200]
ATIS_PERCENTAGES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
ATIS_TYPES = [(1, 'Prevision Atis'),
              (2, 'Real Atis'),
              (3, 'Adherence Atis')]


def parse_args():
    """Parse the command line arguments"""
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--input', type=str,
                    default='src/results/default.json', help='File where the run stats will be saved')
    ap.add_argument('-o', '--output', type=str,
                    default='plots', help='Output directory for the plots')

    return ap.parse_args()


def run_simulation(sp: str, ap=0, n=800, r=10, thr=0.9, tmax=48, tp=None, atis=2):
    """Run a HERMES simulation with the given parameters"""
    simulator(argparse.Namespace(
        atis_percentage=ap,
        congestion_threshold=thr,
        max_run_time=tmax,
        n_runs=r,
        num_actors=n,
        save_path=sp,
        traffic_peaks=tp,
        used_atis=atis,
        verbose=False,
        plots=False
    ))


def get_run_json(source: str):
    """Get the json resultant of a run"""
    with open(source) as fd:
        # File is a one liner
        for line in fd:
            return json.loads(line)


def add_to_dataframe(data: [[float, str, float]], domain: float,
                     atis_type: str, values: (float, float)):
    """Add a row to the dataframe data, for each value:
    avg - std, avg & avg + std"""
    avg, std = values
    for val in [avg, avg + std, avg - std]:
        data.append([domain, atis_type, val])


def atis_percentage_plot(atis: (int, str), source: str, output: str):
    """Plot how different atis percentages affect the simulation performance"""
    atis_yes_times = []
    atis_no_times = []
    a_type, a_name = atis

    for atis_p in ATIS_PERCENTAGES:
        run_simulation(
            ap=atis_p,
            sp=source,
            atis=a_type,
            n=900
        )

        run_stats = get_run_json(source)
        atis_yes_times.append(run_stats['time_atis_yes'])
        atis_no_times.append(run_stats['time_atis_no'])

    df_data = []
    for i in range(len(ATIS_PERCENTAGES)):
        ap = ATIS_PERCENTAGES[i]

        add_to_dataframe(df_data, ap, 'Atis Yes', atis_yes_times[i])
        add_to_dataframe(df_data, ap, 'Atis No', atis_no_times[i])

    df = pd.DataFrame(
        columns=["Atis Percentage", "Atis Type", "Traverse Time"],
        data=df_data
    )

    plt.clf()
    sns.lineplot(x='Atis Percentage', y="Traverse Time",
                 hue="Atis Type", data=df)

    plt.title('%s w/ 900 vehicles' % a_name, loc='left',
              fontsize=12, fontweight=0, color='black')

    if not os.path.exists(output):
        os.makedirs(output)
    plt.savefig('%s/%s.png' % (output, a_name))


def num_vehicles_plot(atis: (int, str), source: str, output: str):
    """Plot how different total number of actors in the simulation affect its performance"""
    atis_yes_times = []
    atis_no_times = []
    a_type, a_name = atis

    for n in NUM_VEHICLES:
        run_simulation(
            n=n,
            sp=source,
            atis=a_type,
            ap=0.4
        )

        run_stats = get_run_json(source)
        atis_yes_times.append(run_stats['time_atis_yes'])
        atis_no_times.append(run_stats['time_atis_no'])

    df_data = []
    for i in range(len(NUM_VEHICLES)):
        n = NUM_VEHICLES[i]

        add_to_dataframe(df_data, n, 'Atis Yes', atis_yes_times[i])
        add_to_dataframe(df_data, n, 'Atis No', atis_no_times[i])

    df = pd.DataFrame(
        columns=["Total Simulation Actors", "Atis Type", "Traverse Time"],
        data=df_data
    )

    plt.clf()
    sns.lineplot(x='Total Simulation Actors', y="Traverse Time",
                 hue="Atis Type", data=df)

    plt.title('%s w/ 0.4 atis users' % a_name, loc='left',
              fontsize=12, fontweight=0, color='black')

    if not os.path.exists(output):
        os.makedirs(output)
    plt.savefig('%s/%s_nVehicles.png' % (output, a_name))


def main():
    args = parse_args()

    sns.set()

    for at in ATIS_TYPES:
        atis_percentage_plot(at, args.input, args.output)
        num_vehicles_plot(at, args.input, args.output)


if __name__ == '__main__':
    main()
