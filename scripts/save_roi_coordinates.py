#@ File (label="Choose where point values will be saved", style="save") file_path

from ij.plugin.frame import RoiManager
import csv

rm = RoiManager.getRoiManager()

#print(rm.getRoisAsArray()[0].getPolygon().xpoints)
#print(rm.getRoisAsArray()[0].getPosition())

columns1 = []
columns2 = []
# The number of columns is the number of rois * 2
n_rois = len(rm.getRoisAsArray())
rows = []

for roi_index, roi in enumerate(rm.getRoisAsArray()):
	frame = roi.getPosition()
	columns1.append(frame) # Create two columns for this frame
	columns1.append(frame)
	columns2.append("x") # One for x points, one for y
	columns2.append("y")
	
	x_points = roi.getPolygon().xpoints
	y_points = roi.getPolygon().ypoints
	
	while len(rows) < len(x_points):
		rows.append([None, None] * n_rois) # Create empty row
	
	for i, (x, y) in enumerate(zip(x_points, y_points)):
		rows[i][roi_index * 2] = x
		rows[i][roi_index * 2 + 1] = y


f = open(str(file_path), "w")
writer = csv.writer(f, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	
writer.writerow(columns1)
writer.writerow(columns2)
for r in rows:
	writer.writerow(r)
f.close()
print("Wrote to points.csv")

	
	