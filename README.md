## Hermes: A Tool for Event-driven Meso Simulation of ATIS
> Systems Modelling & Simulation: The Sharing of Traffic Knowledge

### Usage
```
usage: main.py [-h] [-n N] [-r R] [-thr THRESH] [-tmax MAX_TIME]
               [-atis ATIS_P] [-p TPEAK_MEAN TPEAK_STD] [-o SAVE_PATH] [-ap]
               [-ar] [-aa] [-v]

Systems Modelling and Simulation

optional arguments:
  -h, --help            show this help message and exit
  -n N, --num_actors N  number of vehicles/actors to generate per simulation
                        run
  -r R, --runs R        number of times to run the simulation for
  -thr THRESH, --congestion_threshold THRESH
                        threshold when to consider a link congested,
                        volume/capacity
  -tmax MAX_TIME, --max_run_time MAX_TIME
                        max time of each simulation run (in hours)
  -atis ATIS_P, --atis_percentage ATIS_P
                        percentage of vehicles using the ATIS system
  -p TPEAK_MEAN TPEAK_STD, --peak TPEAK_MEAN TPEAK_STD
                        mean and standard deviation of a normal distribution
                        that represents a peak in traffic
  -o SAVE_PATH, --out_file SAVE_PATH
                        place to save the result of running the simulations
  -ap, --atis-prevision
                        ATIS will make use of predictions to estimate the
                        fastest route
  -ar, --atis-real      ATIS will make use of real times to estimate the
                        fastest route
  -aa, --atis-adherence
                        ATIS will make use of other atis users' data to
                        estimate the fastest route
  -v, --verbose         allow helpful prints to be displayed
  -pl, --plots          display plots at the end of the simulation regarding
                        the network occupation

```

### S'more details
Advanced traveller information systems (ATIS) have seen a recent surge in popularity among urban users.
These systems have the ability to considerably increase traffic flow, across a city's streets but are limited by their penetration ratio among the city's population.

In this work we simulate a road network where different levels of information percolation are tested. The analogy with real life is to assess the extend to which an ATIS can improve total travel time and road utilization, and quantify this usefulness by means of improvements of traffic flow on several metrics.

We out here trying to revolutionize traffic y'all.

### Reproducing Paper Experiments

In the paper, three scenarios are analysed: a __normal scenario__, a __accident scenario__ and a __saturated scenario__, using the __Adherence ATIS__. In the matrix below, when can observe the command used to run the correspondent experiment and its results.

| Scenario | Command | Global Actors distribution | Actors by Edge distribution | Note |
|:-:|:-:|:-:|:-:|:-:|
| Normal Scenario | `python src/main.py -r 100 -atis 0.3 -aa` | ![Normal Global](https://user-images.githubusercontent.com/22712373/60199100-15ef2f80-983b-11e9-93e0-883978e41a2b.png) | ![Normal Scenario](https://user-images.githubusercontent.com/22712373/60199101-15ef2f80-983b-11e9-8408-ac1e7d520268.png) | - |
| Accident Scenario | `python src/main.py -r 100 -atis 0.3 -aa` | ![Accident Global](https://user-images.githubusercontent.com/22712373/60199098-15569900-983b-11e9-9fc8-b5b44033969c.png) | ![Accident Scenario](https://user-images.githubusercontent.com/22712373/60199099-15569900-983b-11e9-99aa-bb24798b5fc1.png) | Create an AccidentEvent at _10:00_ in edge _(3, 6)_ with factor _0.2_ in `simulator.py`, function `create_accident_events()` |
| Saturated Scenairo | `python src/main.py -r 100 -atis 0.3 -aa -n 900`| ![Saturated Global](https://user-images.githubusercontent.com/22712373/60199102-15ef2f80-983b-11e9-9f97-798f1b5b5133.png) | ![Saturated Scenario](https://user-images.githubusercontent.com/22712373/60199103-15ef2f80-983b-11e9-932f-162815fd0452.png) | - |

Additionally, to be able to evaluate the tool performance when varying certain parameters, such as the atis percentage, a __tool wrapper__ was developed in the file `plotter.py`.

This wrapper can be used as in:
```
usage: plotter.py [-h] [-i INPUT] [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        File where the run stats will be saved
  -o OUTPUT, --output OUTPUT
                        Output directory for the plots
```

The obtained graphs when running it are:

| | Real ATIS | Prevision ATIS | Adherence ATIS |
|:-:|:-:|:-:|:-:|
| Varying Atis Percentage | ![Real Atis](https://user-images.githubusercontent.com/22712373/60199200-4cc54580-983b-11e9-809b-3138ea385774.png) | ![Prevision Atis](https://user-images.githubusercontent.com/22712373/60199199-4c2caf00-983b-11e9-8aa8-309b60cdbf95.png) | ![Adherence Atis](https://user-images.githubusercontent.com/22712373/60199196-4c2caf00-983b-11e9-859b-59411f2df981.png) |
| Varying Total Actors in Simulation | ![Real Atis_nVehicles_cropped](https://user-images.githubusercontent.com/22712373/60199227-5a7acb00-983b-11e9-8244-3eba5a5f52ec.png) | ![Prevision Atis_nVehicles_cropped](https://user-images.githubusercontent.com/22712373/60199226-5a7acb00-983b-11e9-84c8-48a8f8690cfb.png) | ![Adherence Atis_nVehicles_cropped](https://user-images.githubusercontent.com/22712373/60199225-5a7acb00-983b-11e9-83cf-8ffc4e4679dd.png) |

### Dependencies

* __NetworkX__: Used for modelling the road network.
* __Numpy__: Used for data handling.
* __Pandas__: Used for data handling.
* __Seaborn__: Used data visualization.
* __Matplotlib__: Used for data visualization.

To install the dependencies, one must run the following commands in a terminal containing `python3`:

* In Mac/ Linux:
```shell
python3  -m venv venv
. venv/bin/activate
pip install -r requirements.txt
python3 generator.py
```

* Windows:
```shell
py -3 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
py -3 generator.py
```

In the end you can deactivate the virtual environment by running:
```shell
deactivate
```

### Demo Video [here](https://youtu.be/DK62_a76SKM)

### Contributors
* [André Cruz](https://github.com/AndreFCruz)
* [Edgar Carneiro](https://github.com/EdgarACarneiro)
* [Xavier Fontes](https://github.com/xfontes42)
