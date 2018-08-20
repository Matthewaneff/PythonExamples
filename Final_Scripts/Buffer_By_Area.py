from arcpy import *
import os, sys
import numpy as np

env.overwriteOutput = True

inputFeature = GetParameterAsText(0)
desc = Describe(inputFeature)
if desc.shapeType != 'Point':
	AddError('Input Feature is not a Point feature')
	sys.exit()
	
inputString = GetParameterAsText(1)
bufferType = GetParameter(2)

outputFeature = GetParameterAsText(3)

''' Perform Calculations And Create Buffer '''

# Convert numeric value to meters

(value, metric) = inputString.split(" ")

if metric.lower() == 'acres':
	area = float(value) * 4046.86
elif metric.lower() == 'ares':
	area = float(value) * 100
elif metric.lower() == 'squaremeters':
	area = float(value)
elif metric.lower() == 'squaremiles':
	area = float(value) * 2589.99 
elif metric.lower() == 'squarekilometers':
	area = float(value) * 1000
else:
	AddError('Areal Unit Not Valid')

if bufferType == True:
	# Use the area provided to derive the radius of the buffer
	radius = np.sqrt(area) / 2
	
	# Create a new feature class
	(folder, file) = os.path.split(outputFeature)
	spaRef = desc.spatialReference
	newFeature = management.CreateFeatureclass(folder, file, "POLYGON", '', '', '', spaRef)
	
	# Create a buffer around the point, determine the extent, and add the extent boundaries to an empty array
	with da.SearchCursor(inputFeature, "SHAPE@") as cursor:
		for row in cursor:
			
			buff = row[0].buffer(radius)
			extent = buff.extent
			
			array = Array()
			array.append(Point(extent.XMin, extent.YMin))
			array.append(Point(extent.XMax, extent.YMin))
			array.append(Point(extent.XMax, extent.YMax))
			array.append(Point(extent.XMin, extent.YMax))
			
			# Insert the array object as a polygon object in the new feature class
			with da.InsertCursor(newFeature, "SHAPE@") as cursor:
				poly = Polygon(array)
				cursor.insertRow([poly])

else:
	# Use the area provided to derive the radius of the buffer
	radius = np.sqrt(area/np.pi)
		
	# Create a new feature class
	analysis.Buffer(inputFeature, outputFeature, "{} meters".format(str(radius)))
