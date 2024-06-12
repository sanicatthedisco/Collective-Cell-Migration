import MigrationUtils as mg
from datetime import date
import numpy as np
import matplotlib.pyplot as plt
from os import path

scale = 4.4053

files_to_use = {
    "0401": ["Water"],
    "0402": ["Apyrase", "Water"],
    "0404": ["Apyrase"],
    "0409": [""]
}

root = path.join("..", "Large wounds", "Rest on slide + coverslip")

exp = mg.load_experiment(root,
                       "Apyrase", "20240402", 
                       0, 400, scale=scale)

cell_width = 20 * scale
dist_bins = list(np.array([0, 1, 3, 4, 5, 6, 7, 8, 100]) * cell_width)

dist_ = []
speed_ = []
for track in exp.tracks:
    dist_.append(track.compute_initial_distance(exp.margin))
    speed_.append(track.compute_trajectory(exp.margin).compute_average_speed())

plt.scatter(dist_,speed_)
plt.title(exp.name)
plt.show()