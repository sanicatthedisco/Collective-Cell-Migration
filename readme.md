# Collective Cell Migration Analysis Utilities
A collection of Fiji scripts and a Python library to analyze collective cell migration data in Clytia Hemisphaerica. \
\
By Jared Lenn \
Malamy Lab, University of Chicago

## Overview
This project has two components. In `scripts` are Fiji scripts which allow for image registration to landmarks and exporting RoI coordinates. In `analysis` are python files which contain utilities for analyzing cell migration tracks stored in TrackMate files.

## Scripts

*Under construction*

## Analysis

### Basic types

- The `Vector2` class represents a point in 2D space and has `x` and `y` properties, as well as a variety of convenience methods for doing linear algebra.
- A `TimePoint` represents a 2D point at some time; these are accessed with `t` (`float`) and `pos` (`Vector2`).
- A `Track` represents a path in 2D space over time; this trajectory is held in `Track.points`, a list of `TimePoint`s.
- A `Trajectory` is a path in 1D space over time. Its data is stored slightly differently, as `times` and `displacements`, lists of `float`s.
- A `Curve` is a path in 2D space with no time component; it holds this path in `Curve.points`, a list of `Vector2`s.

### Usage

First, import the analysis module, like so: \
`import MigrationUtils as mg` \
\
After generating a Trackmate xml file, the cell tracks can be imported into `Track` objects: \
`tracks = mg.tracks_from_xml(path_to_file)` \
\
We can also import the wound margin as a `Curve` object from the csv file. \
`margin = mg.margin_from_csv(path_to_file)`
\
