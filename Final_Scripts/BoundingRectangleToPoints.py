import sys, os, datetime
from arcpy import *

env.overwriteOutput = True

def writeLog(*argv):
	AddMessage(' ')
	AddMessage("===================================================================")
	sVersionInfo = 'BoundingRectangleToPoints.py, v20180124'
	AddMessage('Create Bounding Rectangle Points, {}'.format(sVersionInfo))
	AddMessage("")
	AddMessage("Support: mitchell.fyock@tetratech.com, 303-217-3724")
	AddMessage("")
	AddMessage("Input Feature: {}".format(argv[0]))
	AddMessage("Output Location: {}".format(argv[1]))
	AddMessage("===================================================================")
	AddMessage(" ")

"""
========================================================================
Site_Attribute_Extraction.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
12/14/2017		MF			Created new version of tool
12/20/2017		MF			Added Hydrology function
01/24/2018		MF			Added PLSS function
========================================================================
This script is designed to drastically reduce the amount of working hours
required to gather basic spatial attributes related to the location of
cultural sites.  A single Point feature class, as is an ID field
for the feature class, and an output feature class are the only required
inputs.  All other input datasets are not required for the script to run.
"""

if __name__ == '__main__':

	# Initialize Parameters
	inputFeature = GetParameterAsText(0)
	outputLocation = GetParameterAsText(1)
	createRectangle = GetParameter(2)

	# Write to Log
	writeLog(inputFeature, outputLocation)

	# Create a new point feature class in the designated output location. Use the input feature's spatial reference
	feature = management.CreateFeatureclass(outputLocation, "Extent_Point", "POINT", '', '', '', Describe(inputFeature).spatialReference)

	# Create an insert cursor using the ouput feature
	inscurs = da.InsertCursor(feature, "SHAPE@")

	# Create a search cursor using the input feature
	with da.SearchCursor(inputFeature, "SHAPE@") as cursor:

		# Loop through the rows in the cursor
		for row in cursor:

			# Extract bounding rectangle from row
			extent = row[0].extent

			# Isolate bounding rectangle coordinates
			xMin = extent.XMin
			xMax = extent.XMax
			yMin = extent.YMin
			yMax = extent.YMax

			# Create Points from coordinates
			ll = PointGeometry(Point(xMin, yMin))
			lr = PointGeometry(Point(xMax, yMin))
			ur = PointGeometry(Point(xMax, yMax))
			ul = PointGeometry(Point(xMin, yMax))

			# Insert points into output feature
			for point in [ll, lr, ur, ul]:

				inscurs.insertRow([point])

	del inscurs

	if createRectangle:

		feature = management.CreateFeatureclass(outputLocation, "Extent_Poly", "POLYGON", '', '', '', Describe(inputFeature).spatialReference)

		inscurs = da.InsertCursor(feature, "SHAPE@")

		with da.SearchCursor(inputFeature, "SHAPE@") as cursor:
			for row in cursor:

				array = Array()

				extent = row[0].extent

				xMin = extent.XMin
				xMax = extent.XMax
				yMin = extent.YMin
				yMax = extent.YMax

				array.append(Point(xMin, yMin))
				array.append(Point(xMax, yMin))
				array.append(Point(xMax, yMax))
				array.append(Point(xMin, yMax))

				inscurs.insertRow([Polygon(array)])

		del inscurs
