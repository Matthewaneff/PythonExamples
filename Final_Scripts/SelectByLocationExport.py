from arcpy import *
import os, sys

"""
========================================================================
DataDrivenPagesJoins.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
05/22/2017		MF			Created
========================================================================
This script is designed to perform a simple Select By Location analysis
and export it to a user defined location
"""

env.overwriteOutput = True

inputFeatures = GetParameterAsText(0)
inFC_list = inputFeatures.split(';')

selectionFeature = GetParameter(1)
management.MakeFeatureLayer(selectionFeature, "Selector")

outputLocation = GetParameterAsText(2)
outDesc = Describe(outputLocation)

try:
	locationType = outDesc.workspaceType
except AttributeError:
	locationType = outDesc.datasetType

# Iterate through inputFeatures list
for item in inFC_list:

	# Clean the input datasets (this is referring to ValueTables in arcpy)
	item = item.strip("'")

	itemDesc = Describe(item)

	# Perform selection analysis for shapefile
	if itemDesc.dataType == 'ShapeFile':
		base = os.path.basename(item)
		name = base.split('.')[0]
		management.MakeFeatureLayer(item, "{}".format(name))
		featLayer = management.SelectLayerByLocation("{}".format(name), "INTERSECT", "Selector", '', "NEW_SELECTION")

		# Get row count
		x = management.GetCount(featLayer)
		count = int(x.getOutput(0))

		# If row count is greater than 0, export the feature
		if count > 0:

			# Determine the output location type (folder or gdb) and export accordingly
			if locationType == 'FileSystem':
				conversion.FeatureClassToShapefile("{}".format(name), outputLocation)
			else:
				try:
					conversion.FeatureClassToFeatureClass("{}".format(name), outputLocation, "{}".format(name))
				except:
					conversion.FeatureClassToGeodatabase("{}".format(name),outputLocation)
		management.Delete("{}".format(name))

	# Perform selection analysis for feature class
	elif itemDesc.dataType == 'FeatureClass':
		name = os.path.basename(item)
		management.MakeFeatureLayer(item, "{}".format(name))
		featLayer = management.SelectLayerByLocation("{}".format(name), "INTERSECT", "Selector", '', "NEW_SELECTION")
		x = management.GetCount(featLayer)
		count = int(x.getOutput(0))

		if count > 0:
			if locationType == 'FileSystem':
				conversion.FeatureClassToShapefile("{}".format(name), outputLocation)
			else:
				try:
					conversion.FeatureClassToFeatureClass("{}".format(name), outputLocation, "{}".format(name))
				except:
					conversion.FeatureClassToGeodatabase("{}".format(name),outputLocation)

		management.Delete("{}".format(name))
