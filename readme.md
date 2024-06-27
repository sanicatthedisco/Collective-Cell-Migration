# Collective Cell Migration Analysis Utilities
A collection of Fiji scripts and a Python library to analyze collective cell migration data in Clytia Hemisphaerica. \
\
By Jared Lenn \
Malamy Lab, University of Chicago

## Overview
This project has two components. In `scripts` are Fiji scripts which allow for image registration to landmarks and exporting RoI coordinates. In `analysis` are python files which contain utilities for analyzing cell migration tracks stored in TrackMate files.

If you don't know python, never fear! All of the software in the `analysis` folder has been packaged into a handy google colab project, found here: [JACMAD Software](https://colab.research.google.com/drive/129qx-whFyeDSjB-4Q8JDnjEofPaYcQJE?usp=sharing).

## Scripts

To install a script, locate your Fiji installation directory. 
- On mac: Find the Fiji app, usually in your applications folder. Right-click on it and select "show package contents." 
- On windows: Find the Fiji app's installation site, maybe in C://Program Files. Open the Fiji folder.
  
Open the `scripts` folder and create a new folder called `My scripts`. Drag the script file into this new folder. Now the script is installed! If Fiji is open you will need to restart it.

## Analysis

### Basic types

- The `Vector2` class represents a point in 2D space and has `x` and `y` properties, as well as a variety of convenience methods for doing linear algebra.
- A `TimePoint` represents a 2D point at some time; these are accessed with `t` (`float`) and `pos` (`Vector2`).
- A `Track` represents a path in 2D space over time; this trajectory is held in `Track.points`, a list of `TimePoint`s.
- A `Trajectory` is a path in 1D space over time. Its data is stored slightly differently, as `times` and `displacements`, lists of `float`s.
- A `Curve` is a path in 2D space with no time component; it holds this path in `Curve.points`, a list of `Vector2`s.
- An `Experiment` holds all of the data parsed from a single wound movie. It has `tracks` and a `margin`.

### Usage

First, import the analysis module, like so:
```python
import MigrationUtils as mg
```
After generating a Trackmate xml file, the cell tracks can be imported into `Track` objects:
```python
tracks = mg.tracks_from_xml(path_to_file)
```
We can also import the wound margin as a `Curve` object from the csv file.
```python
margin = mg.margin_from_csv(path_to_file)
```
We can calculate the initial distance of a track from the wound margin like so:
```python
my_track = tracks[0]
my_track.compute_initial_distance(margin)
```
We can also flatten the track into a 1D `Trajectory`.
```python
my_trajectory = my_track.compute_trajectory(margin)
```
Behind the scenes, this function is determining the vector along which the track's starting position is closest to the wound margin. It then projects every point in the track onto this vector to give a 1D representation of how far the cell has crawled in the direction of the wound. \
\
We can plot this trajectory easily: 
```python
import matplotlib.pyplot as plt
plt.plot(my_trajectory.times, my_trajectory.displacements)
```
If you're comparing multiple trajectories, you might want to resample them so that they all have the same time values. A built-in function can do this for you by linear interpolation:
```python
# Resample this trajectory so that it starts at time 0, ends at time 200, and has 100 time steps.
my_trajectory.resample(num_samples=100, min_time=0, max_time=200)
```

You can also extract the average speed of a trajectory:
```python
speed = my_trajectory.compute_average_speed()
# Optionally, you can supply start and end times 
# to compute the average speed only within specific bounds
bounded_speed = my_trajectory.compute_average_speed(start=20, end=180)
```

Let's plot the average speed of all of our tracks together!
```python
dists = [] # An array to hold the initial distances of each cell
speeds = [] # An array to hold the average speed of each cell

for track in tracks:
    dists.append(track.compute_initial_distance(margin))
    speeds.append(track.compute_trajectory(margin).compute_average_speed())

plt.scatter(dists, speeds)
```
