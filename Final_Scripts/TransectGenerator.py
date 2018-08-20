from arcpy import *
import numpy as np
import os, sys, datetime

def convert_unit(lenUnit):
	unit = lenUnit.lower()

	if unit == 'meters':
		unit = 'meter'
	elif unit == 'feet':
		unit = 'foot'

	return unit

#####################################################################################################

def Create_Transects(extent, tempFile):
	
	global surveyAngle
	global spacing
	global personnel
	
	# Gather feature extent
	if surveyAngle == 90:
	
		xMin = extent.XMin
		yMin = extent.YMin
		xMax = extent.XMax
		yMax = extent.YMax - spacing
		
	elif surveyAngle == 0 or surveyAngle == 180:
		
		xMin = extent.XMin + spacing
		yMin = extent.YMin
		xMax = extent.XMax
		yMax = extent.YMax
	
	else:
		xMin = extent.XMin
		yMin = extent.YMin
		xMax = extent.XMax
		yMax = extent.YMax
	
	coordinates = []

	if surveyAngle == 90:

		yInt = (spacing * (personnel + 1))

		# Calculate the number of points needed to cover the extent
		iteration = int(np.sqrt((xMax - xMin)**2 + (yMax - yMin)**2)/ ((personnel + 1) * spacing)) + 1

		array = Array()
		array.add(Point(xMin, yMax))
		array.add(Point(xMax, yMax))
		coordinates.append(array)

		for i in range(iteration):
			array = Array()
			yy = yMax - (yInt * i)
			array.add(Point(xMin, yy))
			array.add(Point(xMax, yy))
			coordinates.append(array)

	elif surveyAngle == 0 or surveyAngle == 180:

		xInt = (spacing * (personnel + 1))

		# Calculate the number of points needed to cover the extent
		iteration = int(np.sqrt((xMax - xMin)**2 + (yMax - yMin)**2)/ ((personnel + 1) * spacing)) + 1

		array = Array()
		array.add(Point(xMin, yMin))
		array.add(Point(xMin, yMax))
		coordinates.append(array)

		for i in range(iteration):
			array = Array()
			xx = xMin + (xInt * i)
			array.add(Point(xx, yMin))
			array.add(Point(xx, yMax))
			coordinates.append(array)

	else:

		surveyAngle = np.deg2rad(surveyAngle)

		yInt = np.abs((spacing * (personnel + 1)) / np.sin(surveyAngle))
		xInt = np.abs((spacing * (personnel + 1)) / np.sin(abs(np.pi/2 - surveyAngle)))

		if surveyAngle < np.pi/2:

			# Calculate the number of points needed to cover the extent
			iteration = int(np.sqrt((xMax - xMin)**2 + (yMax - yMin)**2)/ ((personnel + 1) * spacing)) + 1

			for i in range(iteration):
				array = Array()
				xx = xMin + (xInt * i)
				yy = yMax - (yInt * i)
				array.add(Point(xMin, yy))
				array.add(Point(xx, yMax))
				coordinates.append(array)

		else:

			# Calculate the number of points needed to cover the extent
			iteration = int(np.sqrt((xMax - xMin)**2 + (yMax - yMin)**2)/ ((personnel + 1) * spacing)) + 1

			for i in range(iteration):
				array = Array()
				xx = xMin + (xInt * i)
				yy = yMin + (yInt * i)
				array.add(Point(xMin, yy))
				array.add(Point(xx, yMin))
				coordinates.append(array)
	
	with da.InsertCursor(tempFile, "SHAPE@") as cursor:

			for item in coordinates:
				shape = Polyline(item).clip(extent)
				cursor.insertRow([shape])			


"""
========================================================================
Transect Spacing
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
03/20/2017		MF			Created
06/29/2017		MF			Added boolean option enabling for clipping or non-clipping of final output
07/28/2017		MF			Modified Exports
========================================================================
This script is designed to create transect lines at specific user-defined
angles using a user-defined spacing interval.
"""

'''Initialize Parameters and Perform Checks'''
	
# Gathers input feature from user
inFeature = GetParameterAsText(0)
spatialRef = Describe(inFeature).spatialReference

# Gathers number of personnel used for survey
personnel = GetParameterAsText(1)
try:
	personnel = int(personnel)
except ValueError:
	AddError("Personnel Count must be numeric")
	sys.exit()

# Gathers transect spacing for survey
spacing = GetParameterAsText(2)
(spacingInterval, spacingUnit) = spacing.split(' ')
try:
	spacing = int(spacingInterval)
except ValueError:
	AddError("Spacing Interval must be numeric")
	sys.exit()

# Check Projection and Linear Units
linearUnit = convert_unit(spacingUnit)
if linearUnit != spatialRef.linearUnitName.lower():
	AddError('Linear Unit and Projection Unit do not match')
	AddError('Linear Unit: {} | Projection Unit: {}'.format(spatialRef.linearUnitName.title(), spacingUnit.title()))
	sys.exit()

# Create output feature
try:
	surveyAngle = float(GetParameterAsText(3))
	if surveyAngle < 0 or surveyAngle > 180:
		AddError("Angle is out of range")
		sys.exit()
except:
	AddError("Angle must be numeric")
	sys.exit()

# Create output feature
outFeature = GetParameterAsText(4)
(Folder, Feature) = os.path.split(outFeature)
temp = management.CreateFeatureclass("in_memory", "temp", "Polyline", '', '', '', spatialRef)

# Write to log
d = datetime.datetime.now()
sDate = d.strftime("%Y%m%d")
AddMessage(sDate)
AddMessage("===================================================================")
sVersionInfo = 'TransectGenerator.py, v20170728'
AddMessage('Pedestrian Survey Transect Generator, {}'.format(sVersionInfo))
AddMessage("")
AddMessage("Support: mitchell.fyock@tetratech.com, 303-2173724")
AddMessage("")
AddMessage("Input Feature: {}".format(inFeature))
AddMessage("Personnel Number: {}".format(personnel))
AddMessage("Spacing Interval: {} {}".format(str(spacingInterval), spacingUnit))
AddMessage("Survey Angle: {}".format(surveyAngle))
AddMessage("Output Location: {}".format(outFeature))
AddMessage("===================================================================")			


# Create transects and insert them into the temp file
with da.SearchCursor(inFeature, "SHAPE@") as mainCurs:
	for r in mainCurs:
		Create_Transects(r[0].extent, temp)

'''Write Final Features'''

# Create Final Feature Class
analysis.Clip(temp, inFeature, outFeature)
management.Delete(temp)
