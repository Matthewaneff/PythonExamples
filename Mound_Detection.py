from arcpy import *
import os, sys

inputFeature = ''
inputField = ''
outputFeature = ''
(outputFolder, outputName) = os.path.split(outputFeature)

id_list = []

with da.SearchCursor(inputFeature, ['SHAPE@', inputField]) as cursor:
	for row in cursor:
		
		# Find the extent the feature
		extent = row[0].extent
		
		xMin = extent.XMin
		xMax = extent.XMax
		yMin = extent.YMin
		yMax = extent.YMax
		
		# Enter a conditional test to identify if the length/width of the feature extent is within the given range
		if (yMax - yMin) > 3 and (yMax - yMin) < 5 and (xMax - xMin) > 3 and (xMax - xMin) < 5:
			
			# If feature is within length/width requirements, add the Feature ID to the ID list
			id_list.append(row[2])


# Make a Feature Layer that can be queried
management.MakeFeatureLayer(inputFeature, "Input Feature")

# Select from the Layer all features whose ID is in the ID list
management.SelectLayerByAttribute("Input Feature", "NEW_SELECTION", "{} IN ({})".format(inputField, id_list))

# Export the layer as a new Feature Class
conversion.FeatureClassToFeatureClass("Input Feature", outputFolder, outputName)
