import os, sys, datetime
from arcpy import *

def writeLog(*argv):
	AddMessage(' ')
	AddMessage("===================================================================")
	sVersionInfo = 'Create_Rectangle_From_Feature.py, v20180308'
	AddMessage('Create Rectangle From Feature, {}'.format(sVersionInfo))
	AddMessage("")
	AddMessage("Support: mitchell.fyock@tetratech.com, 303-217-3724")
	AddMessage("")
	AddMessage("Input Featureclass: {}".format(argv[0]))
	AddMessage("STP Spacing: {} {}".format(argv[1], argv[2]))
	AddMessage("Output Featureclass: {}".format(argv[3]))
	AddMessage("===================================================================")
	AddMessage(" ")

"""
========================================================================
Points_Along_Line.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
04/06/2018		MF			Created
========================================================================
This tool has been created to automate the creation of STP locations
along linear features
"""

def main():

	# Set environment settings
	env.overwriteOutput = True

	# Initialize Parameters
	inputFeature = GetParameterAsText(0)
	desc = Describe(inputFeature)

	# Perform cursory check on input feature
	if desc.shapeType == 'Point':
		
		# If shapetype is point, add error message and stop script
		AddError('Input Feature must be Polygon or Polyline')
		sys.exit()

	spacingInterval, spacingUnit = GetParameterAsText(1).split(' ')
	spacingInterval = int(spacingInterval)
	outputFeature = GetParameterAsText(2)
	
	# Write to Log
	writeLog(inputFeature, spacingInterval, spacingUnit, outputFeature)

	# Create new feature
	outDir, outName = os.path.split(outputFeature)
	outputFeature = management.CreateFeatureclass(outDir, outName, "POINT", '', '', '', desc.spatialReference)
	fields = ['STP_ID', 'STP_Status', 'STP_Result']
	[management.AddField(outputFeature, "{}".format(i), "TEXT") for i in fields]

	# Create Insert Cursor object
	inscurs = da.InsertCursor(outputFeature, ["SHAPE@", "STP_ID"])

	if desc.shapeType == 'Polyline':
		pass
	else:
		inputFeature = management.FeatureToLine(inputFeature, "in_memory/temp")

	# Create Search Cursor object
	with da.SearchCursor(inputFeature, "SHAPE@") as cursor:
		count = 0
		for row in cursor:
			
			# Collect the length of the feature
			rowLength = row[0].getLength()
			
			# Divide feature length by spacing interval
			spacing = int(rowLength/spacingInterval)
			
			# Loop through index range from the result of dividing the feature lenght by the spacing interval
			for i in range(spacing + 1):
				
				# Create a point by multiplying the index number by the spacing interval and insert it into the Insert Cursor object
				point = row[0].positionAlongLine((i*spacingInterval), False)
				inscurs.insertRow([point, 'STP_{}'.format(count)])

	# Delete the Insert Cursor object and the temporary object
	del inscurs
	management.Delete(inputFeature)

if __name__ == '__main__':
	main()
