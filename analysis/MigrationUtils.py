from __future__ import annotations
import xml.etree.ElementTree as ET
from math import sqrt
import pandas as pd
import numpy as np
from scipy.signal import resample
from matplotlib.collections import LineCollection
import matplotlib.pyplot as plt
from datetime import date
from typing import Generator
import math
from os import path

from Math import Vector2 as V2, Curve

DEFAULT_SCALE = 4.4053

# *******
# Classes
# *******

class TimePoint():
    def __init__(self, time: float, position: V2):
        self.t = time
        self.pos = position
    def __repr__(self):
        return "(" + str(round(self.t)) + ", " + str(round(self.pos.x)) + ", " + str(round(self.pos.y)) + ")"

class Track():
    def __init__(self, points: list[TimePoint]):
        self.points = points

    def add_point(self, point: TimePoint):
        self.points.append(point)
    
    def sort_and_remove_duplicates(self):
        # TODO: this is inefficient and should be fixed
        sorted_points = sorted(self.points, key=lambda p: p.t)
        no_duplicates = [p for i, p in enumerate(sorted_points) 
                           if sorted_points.index(p) == i]
        return Track(no_duplicates)
    
    def project_onto_line(self, p1, p2) -> Trajectory:
        t_ = [tp.t for tp in self.points]
        x_ = [tp.pos.project_onto_line(p1, p2) for tp in self.points]
        return Trajectory(list(t_), list(x_))
    
    # Projects onto curve to flatten into trajectory
    def compute_trajectory(self, margin: Curve) -> Trajectory:
        track_start = self.points[0].pos
        closest_margin_point = track_start.closest_point_on_curve(margin)
        projected_track = self.project_onto_line(track_start, closest_margin_point)
        return projected_track
    
    def compute_initial_distance(self, margin: Curve) -> float:
        first_point = self.points[0].pos
        perp_point = first_point.closest_point_on_curve(margin)
        return (first_point - perp_point).magnitude()
    
    def get_positions_in_long_form(self) -> tuple[list[float], list[float]]:
        x_ = [pt.pos.x for pt in self.points]
        y_ = [pt.pos.y for pt in self.points]
        return (x_, y_)
    
    def get_times(self) -> list[float]:
        return [pt.t for pt in self.points]

# A flattened version of a track with only times and displacements
# points are in long form unlike Track for convenience
class Trajectory():
    def __init__(self, times: list[float], displacements: list[float]):
        self.times = times
        self.displacements = displacements
    
    def get_data(self):
        return (self.times, self.displacements)

    def resample(self, num_samples: int, min_time: float, max_time: float):
        interp_t = list(np.linspace(min_time, max_time, num_samples, endpoint=False))
        interp_x = list(np.interp(interp_t, self.times, self.displacements))
        return Trajectory(interp_t, interp_x)
    
    def compute_average_speed(self, start=0, end=math.inf) -> float:
        trunc_times = []
        trunc_disps = []
        for t, d in zip(self.times, self.displacements):
            if t >= start and t <= end:
                trunc_times.append(t)
                trunc_disps.append(d)
        speed, _ = np.polyfit(trunc_times, trunc_disps, 1)
        return speed

# Represents all of the data from a single movie of a wound
class Experiment():
    def __init__(self, tracks: list[Track], margin: Curve, 
                 condition: str="", date: str="",
                 start_time: float=0, end_time: float=math.inf, index:int=0):
        # evil list comp lol
        self.tracks = [
            Track([pt for pt in track.points 
                if pt.t >= start_time and pt.t <= end_time])
            for track in tracks
        ]
        self.margin = margin
        self.name = condition + str(date)
    
    def bin_tracks(self, dist_bins: list[float]) -> list[dict]:
        def _internal():
            for i in range(len(dist_bins)-1):
                tracks = find_tracks_in_range(self.tracks, self.margin, dist_bins[i], dist_bins[i+1])
                if len(tracks) > 0:
                    yield {
                        "start": dist_bins[i],
                        "end": dist_bins[i+1],
                        "tracks": find_tracks_in_range(self.tracks, self.margin, dist_bins[i], dist_bins[i+1])
                    }
        return list(_internal())

    def to_trajectories(self, tracks: list[Track], num_samples=100, min_time=0, max_time=200) -> list[Trajectory]:
        def _internal():
            for track in tracks:
                yield track.compute_trajectory(self.margin).resample(num_samples, min_time, max_time)
        return list(_internal())

# *******
# Parsing
# *******

# Parse data from trackmate
def tracks_from_xml(file_path: str, scale:float=DEFAULT_SCALE) -> list[Track]:
    # Get and parse file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Loop through spots and add to dictionary by ID
    spots = {}
    for s in root.findall(".//Spot"):
        spots[s.get("ID")] = s
    
    # Tracks reference spot IDs
    # Go through track edges, find corresponding spots from dictionary
    # and make new tracks from these
    tracks: list[Track] = []
    for track_data in root.findall(".//Track"):
        track = Track([])
        for edge in track_data:
            edge_spots = [spots[edge.get("SPOT_SOURCE_ID")],
                           spots[edge.get("SPOT_TARGET_ID")]]
            
            for spot in edge_spots:
                track.add_point(
                    TimePoint(
                        float(spot.get("FRAME")),
                        V2(
                            float(spot.get("POSITION_X"))*scale, 
                            float(spot.get("POSITION_Y"))*scale
                        )
                    )
                )
        
        # Bit of a hack sorry -- the points come out unsorted and with some dupes
        tracks.append(track.sort_and_remove_duplicates())
    
    return tracks

# Parse margin data from roi export script
def margin_from_csv(file_path: str) -> Curve:
    margin_data = pd.read_csv(file_path)
    margin_x = [float(_) for _ in margin_data["1"][1:]]
    margin_y = [float(_) for _ in margin_data["1.1"][1:]]

    points = []
    for x, y in zip(margin_x, margin_y):
        points.append(V2(x, y))

    return Curve(points)

def load_experiment(root_path: str, condition: str, date: str, start_time: float, end_time: float, scale:float=1):
    track_path = path.join(root_path, date, date + condition + "_tracking.xml")
    margin_path = path.join(root_path, date, date + condition +  "_margin.csv")
    tracks = tracks_from_xml(track_path, scale)
    margin = margin_from_csv(margin_path)
    return Experiment(tracks, margin, condition, date, start_time, end_time)

# *********
# Utilities
# *********

# Determines all tracks for which their first point in time is within the specified
# distance from the wound margin
def find_tracks_in_range(tracks: list[Track], margin: Curve, min_distance: float, max_distance: float) -> list[Track]:
    tracks_in_range = []
    for track in tracks:
        initial_dist = track.compute_initial_distance(margin)
        if initial_dist >= min_distance and initial_dist < max_distance:
            tracks_in_range.append(track)
    
    return tracks_in_range

def average_trajectories(trajectories: list[Trajectory]) -> Trajectory:
    disps_ = [traj.displacements for traj in trajectories]
    mean_disps = np.mean(disps_, axis=0)
    # assumes that trajectories all have same times.
    # i.e. resample before using this method
    # should fix
    return Trajectory(trajectories[0].times, mean_disps)

# *************
# Visualization
# *************

def plot_tracks_by_bin(tracks, margin, dist_bins, colors, fig, ax):
    for i in range(len(dist_bins)-1):
        tracks_in_bin = find_tracks_in_range(tracks, margin, dist_bins[i], dist_bins[i+1])
        for track in tracks_in_bin:
            x_, y_ = track.get_positions_in_long_form()
            ax.plot(x_, y_, c=colors[i])
    
    ax.plot(margin[0], margin[1])

"""
def plot_tracks(tracks: list[Track], margin: Curve, fig, ax):
    for track in tracks:
        x, y = track.positions_to_long_form()
        t = track.get_times()

        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        # Create a LineCollection object
        lc = LineCollection(segments, array=t)
        lc.set_array(t)  # Set the color values based on the third variable

        ax.add_collection(lc)
        ax.autoscale()
        #plt.colorbar(lc, label='t')
        plt.xlabel('X')
        plt.ylabel('Y')

    fig.colorbar(lc)
    plt.cm.viridis(1.5)
    plt.plot(margin[0], margin[1], c="red")
"""