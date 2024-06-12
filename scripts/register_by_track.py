from fiji.plugin.trackmate.io import TmXmlReader
from fiji.plugin.trackmate import Logger, Spot
from java.io import File
from ij import IJ
from ij.gui import OvalRoi, Line
import sys

# -- These aren't comments they're imageJ parameter commands --

#@ File (label="Choose a trackmate xml file containing the track to register to", style="open") registration_track_file
#@ int (label="Reference frame") REFERENCE_FRAME
#@ boolean (label="Draw the track as an overlay on this image?") DRAW_OVERLAY
#@ boolean (label="Get spots instead of tracks") NO_TRACKS

# -------------------------------------------------------------

#Scale factor
s = 1

def interpolate(x1, y1, x2, y2, x):
	m = (y2 - y1)/(x2 - x1)
	b = y1 - (m * x1)
	return (m * x) + b

prev_frame = 0
def draw_overlay(x_offsets, y_offsets, frames, t, imp):
	global s, prev_frame
	roi = OvalRoi((x_offsets[frames.index(t)]-5)*s, (y_offsets[frames.index(t)]-5)*s, 10*s, 10*s)

	if not prev_frame == 0:
		ov = imp.getOverlay()
		line = Line(x_offsets[frames.index(t)]*s, y_offsets[frames.index(t)]*s, 
					x_offsets[frames.index(prev_frame)]*s, y_offsets[frames.index(prev_frame)]*s)
		ov.add(line)
		ov.add(roi)
		imp.setOverlay(ov)
		imp.show()
	
	prev_frame = t

# Stupid custom trackmate parsing
def get_tracks_from_file(file_path):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	file = File(file_path)
	logger = Logger.IJ_LOGGER
	reader = TmXmlReader(file)
	if not reader.isReadingOk():
		sys.exit( reader.getErrorMessage() )
	model = reader.getModel()

	ids = list(model.getTrackModel().trackIDs(True))
	tracks = [model.getTrackModel().trackSpots(id) for id in ids]
	
	return tracks

def get_spots_from_file(file_path):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	file = File(file_path)
	logger = Logger.IJ_LOGGER
	reader = TmXmlReader(file)
	if not reader.isReadingOk():
		sys.exit( reader.getErrorMessage() )
	model = reader.getModel()
	
	return list(model.getSpots().iterable(False))

def main():
	# Get currently active image stack to operate on
	imp = IJ.getImage()
	size = imp.getStackSize()

	# Get scale data from image calibration
	s = 1/imp.getCalibration().pixelWidth
	print(s)

	if NO_TRACKS:
		track = get_spots_from_file(str(registration_track_file))
	else:
		track = get_tracks_from_file(str(registration_track_file))[0]

	# Get relevant offset data from spots in track
	# Frames are returned zero indexed even though imageplus uses them 1-indexed. ????
	frames = [spot.getFeature("FRAME") + 1 for spot in track]
	x_offsets = [spot.getFeature("POSITION_X") * s for spot in track]
	y_offsets = [spot.getFeature("POSITION_Y") * s for spot in track]

	#Dumb BS to sort properly. Prob should fix
	frames_sorted = sorted(frames)
	x_offsets_sorted = []
	y_offsets_sorted = []
	for f in frames_sorted:
		x_offsets_sorted.append(x_offsets[frames.index(f)])
		y_offsets_sorted.append(y_offsets[frames.index(f)])
	frames = frames_sorted
	x_offsets = x_offsets_sorted
	y_offsets = y_offsets_sorted

	# Register to reference frame as template
	x_0 = x_offsets[REFERENCE_FRAME]
	y_0 = y_offsets[REFERENCE_FRAME]

	print(zip(frames, x_offsets, y_offsets))

	# Loop through all frames
	for t in range(1, size + 1):
		# 	If this frame has been explicitly assigned an offset
		# in the track, just correct by that offset
		if t in frames:
			offset_x = x_0 - x_offsets[frames.index(t)]
			offset_y = y_0 - y_offsets[frames.index(t)]

			if DRAW_OVERLAY:
				draw_overlay(x_offsets, y_offsets, frames, t, imp)
		# 	If this frame is in between assigned frames,
		# linearly interpolate between the closest recorded frames
		# to determine what the offset should be.
		else:
			# Find first recorded frame ahead of the current frame
			for f_i, f in enumerate(frames):
				if t - f < 0:
					# Find the recorded frame right before that
					t_upper = f
					t_lower = frames[f_i-1]
					
					# Linearly interpolate offset between these two points
					x_lower = x_offsets[frames.index(t_lower)]
					x_upper = x_offsets[frames.index(t_upper)]
					x = interpolate(t_lower, x_lower, t_upper, x_upper, t)
					
					y_lower = y_offsets[frames.index(t_lower)]
					y_upper = y_offsets[frames.index(t_upper)]
					y = interpolate(t_lower, y_lower, t_upper, y_upper, t)
					
					offset_x = x_0 - x
					offset_y = y_0 - y
					break
					
		# Transform this frame by the offset we found
		imp.setPosition(t)
		ip = imp.getProcessor()
		ip.translate(offset_x, offset_y)
		imp.setProcessor(ip)
		imp.show()

if __name__ == "__main__":
	main()