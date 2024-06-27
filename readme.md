# Collective Cell Migration Analysis Utilities
A collection of Fiji scripts and a Python library to analyze collective cell migration data in Clytia Hemisphaerica. \
\
By Jared Lenn \
Malamy Lab, University of Chicago

## Overview
This project has two components. In `scripts` are Fiji scripts which allow for image registration to landmarks and exporting RoI coordinates. In `analysis` are python files which contain utilities for analyzing cell migration tracks stored in TrackMate files.

If you don't know python, never fear! All of the software in the `analysis` folder has been packaged into a handy google colab project, found here: [JACMAS Software](https://colab.research.google.com/drive/129qx-whFyeDSjB-4Q8JDnjEofPaYcQJE?usp=sharing).

## Scripts

To install a script, locate your Fiji installation directory. 
- On mac: Find the Fiji app, usually in your applications folder. Right-click on it and select "show package contents." 
- On windows: Find the Fiji app's installation site, maybe in C://Program Files. Open the Fiji folder.
  
Open the `scripts` folder and create a new folder called `My scripts`. Drag the script file into this new folder. Now the script is installed! If Fiji is open you will need to restart it.

## Analysis

Again, this software has been packaged in the [JACMAS Software](https://colab.research.google.com/drive/129qx-whFyeDSjB-4Q8JDnjEofPaYcQJE?usp=sharing) on google colab. For those that know Python, a summary of the types and functions I have implemented for track analysis is given below.

To use either version of the software, you will need to create two configuration files. I set it up this way because I analyzed my data blinded. You don't have to do the same (although it is convenient this way!). The metadata file has everything you record about the movie while you're blinded, while the key file corresponds movie IDs to their conditions so you don't have to know what each ID is.

*A note on units: I conducted all of my analysis in pixels and frames, and then converted at the very end to microns and seconds. I know this sucks and I'm sorry. It creates a few problems that I'm forseeing being annoying. First, the margin ROIs get exported in pixels, while the trackmate measurements are exported in whatever units your tiff file is set to. For me, all of my tiff files were off from the pixel value by a factor of 2. I created two parameters to deal with this which are explained in the colab.*

#### Metadata
This file can be called anything -- I'll refer to it as `metadata.csv`. In a program like excel or sheets, create a new spreadsheet with the following columns: `movie_id`, `start_time`, `stop_time`, `is_excluded`, `linear_start_time`, and `linear_stop_time`. (Everything is case sensitive!) You can also include other columns for your own bookkeeping; only those with the above names are read by the software. Each row corresponds to the metadata for a given cell migration movie. Populate each row with the following information for each column:

- `movie_id`: This is whatever you have chosen to name your csv and xml files for the movies. I used numbers, but it can be text if you'd like (if that crashes the program use numbers though).
- `start_time`: Often movies begin with some time you don't want to record. Put the start time, in whatever time units your movie uses, in this cell.
- `stop_end`: Same as start time, just where you'd like the movie to end.
- `is_excluded`: You can put a "Y" in this column if you'd like to exclude a movie from analysis; otherwise, leave it blank.
- `linear_start_time`: This is the start cutoff for linear interpolation; you can use it to specify the range in which the data is relatively linear so the software will only calculate speeds within this range. These should be in seconds, or whatever unit you've set the software to convert everything into.
- `linear_stop_time`: Same as above, the end time for linear interpolation.

#### Key
Create a seperate spreadsheet with the following columns: `date`, `condition`, `index`, and `movie_id`:
- `date` is the date on which the movie was taken
- `condition` is the experimental condition of the movie
- `index`: in case you took multiple movies of the same condition on the same day, you can number them with `index`.
- `movie_id`: the same as `movie_id` in your `metadata.csv` file and as in the names of your `.xml` and `.csv` files.

See examples in `analysis/examples`.

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
