import os, sys, datetime
from arcpy import *

env.overwriteOutput = True

def writeLog(*argv):
	AddMessage(' ')
	AddMessage("===================================================================")
	sVersionInfo = 'Create_Rectangle_From_Feature.py, v20180308'
	AddMessage('Create Rectangle From Feature, {}'.format(sVersionInfo))
	AddMessage("")
	AddMessage("Support: mitchell.fyock@tetratech.com, 303-217-3724")
	AddMessage("")
	AddMessage("Input Featureclass: {}".format(argv[0]))
	AddMessage("Output Featureclass: {}".format(argv[1]))
	AddMessage("===================================================================")
	AddMessage(" ")

"""
========================================================================
Create_Rectangle_From_Feature.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
03/08/2018		MF			Created
========================================================================
This script is designed to create bounding rectangles using the original
feature's geographic extent and export this as a new featureclass
"""


if __name__ == '__main__':
	
	# Initialize Parameters
	inputFeature = GetParameterAsText(0)
	outputFeature = GetParameterAsText(1)
	desc = Describe(inputFeature)
	
	# Perform geometry check
	if desc.shapeType != 'Polygon':
		AddError('Input Feature Must Have Polygon Geometry')
		sys.exit()
	
	# Write log
	writeLog(inputFeature, outputFeature)
	
	# Create new featureclass
	folder, fileName = os.path.split(outputFeature)
	newFeature = management.CreateFeatureclass(folder, fileName, 'Polygon', inputFeature, '', '', desc.spatialReference)
	
	# Collect fields from input feature; add 'SHAPE@' field for geometry
	fields = [i.name for i in ListFields(inputFeature)]
	fields.insert(0, 'SHAPE@')
	
	# Create insert cursor using the new featureclass and the fields
	inscurs = da.InsertCursor(newFeature, fields)
	
	# Loop through input featureclass collecting attributes and insert them into new featureclass
	with da.SearchCursor(inputFeature, fields) as cursor:
		for row in cursor:
			
			# Create an empty list to hold the attribute values for the row
			nRow = []
			
			for i in range(len(fields)):
				nRow.append(row[i])
			
			# Insert row into new feature class
			inscurs.insertRow(nRow)
	
	# Delete insert cursor
	del inscurs
	
	# Create an update cursor to loop through each row in the new featureclass
	with da.UpdateCursor(newFeature, 'SHAPE@') as cursor:
		for row in cursor:
			
			# Isolate geographic extent of row
			extent = row[0].extent
			
			# Create an empty array and add extent coordinates
			array = Array()
			array.append(Point(extent.XMin, extent.YMin))
			array.append(Point(extent.XMax, extent.YMin))
			array.append(Point(extent.XMax, extent.YMax))
			array.append(Point(extent.XMin, extent.YMax))
			
			# Change the geometry of the original row to the extent geometry
			row[0] = Polygon(array)
			
			# Update row
			cursor.updateRow(row)			
