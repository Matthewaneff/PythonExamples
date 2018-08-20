import os, sys, datetime
from arcpy import *

def writeLog(*argv):
	AddMessage(' ')
	AddMessage("===================================================================")
	sVersionInfo = 'SHPO_Survey_Deliverable.py, v20180109'
	AddMessage('Generate SHPO Survey Deliverable, {}'.format(sVersionInfo))
	AddMessage("")
	AddMessage("Support: mitchell.fyock@tetratech.com, 303-217-3724")
	AddMessage("")
	AddMessage("Input Feature: {}".format(argv[0]))
	AddMessage("Output Location: {}".format(argv[1]))
	AddMessage("===================================================================")
	AddMessage(" ")

"""
========================================================================
SHPO_Survey_Deliverable.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
01/09/2018		MF			Created
========================================================================
This script is designed to quickly produce the standard SHPO featureclass
deliverable for the Colorado State Historic Preservation Office
"""

if __name__ == '__main__':
	env.overwriteOutput = True

	d = datetime.datetime.now()
	sDate = d.strftime("%m/%d/%Y")

	# Collect Inputs
	inputFeature = GetParameterAsText(0)
	if Describe(inputFeature).shapeType != 'Polygon':
		AddError('Input Featureclass is not a Polygon')
		sys.exit()
	
	outputFeature = GetParameterAsText(1)
	reportAuthor = GetParameterAsText(2)
	reportTitle = GetParameterAsText(3)
	surveyType = GetParameterAsText(4)
	
	siteCount = GetParameterAsText(5)
	if siteCount.isnumeric() == False:
		AddError('Site Count entry is not numeric')
		sys.exit()
		
	ifCount = GetParameterAsText(6)
	if ifCount.isnumeric() == False:
		AddError('Isolated Find Count entry is not numeric')
		sys.exit()
		
	elCount = GetParameterAsText(7)
	if elCount.isnumeric() == False:
		AddError('Eligible Site Count entry is not numeric')
		sys.exit()

	zone = GetParameterAsText(8)
	if zone.isnumeric() == False:
		AddError('UTM Zone entry is not numeric')
		sys.exit()		

	# Write to Log
	writeLog(inputFeature, outputFeature)

	# Create Featureclass
	fc = management.CreateFeatureclass(os.path.dirname(outputFeature), os.path.basename(outputFeature), "POLYGON", '', '', '', Describe(inputFeature).spatialReference)

	# Add Fields
	management.AddField(fc, "AGENCY_", "TEXT")
	management.AddField(fc, "DOC_", "TEXT")
	management.AddField(fc, "AUTHOR", "TEXT")
	management.AddField(fc, "TITLE", "TEXT")
	management.AddField(fc, "SURV_TYPE", "TEXT")
	management.AddField(fc, "SITE_COUNT", "SHORT")
	management.AddField(fc, "IF_COUNT", "SHORT")
	management.AddField(fc, "EL_COUNT", "SHORT")
	management.AddField(fc, "ZONE", "SHORT")
	management.AddField(fc, "X", "LONG")
	management.AddField(fc, "Y", "LONG")
	management.AddField(fc, "ACRES", "DOUBLE")
	management.AddField(fc, "DATE", "DATE")
	management.AddField(fc, "CONF", "TEXT")
	management.AddField(fc, "SOURCE", "TEXT")
	management.AddField(fc, "COMMENTS", "TEXT")

	# Loop through the inputFeature and extract the shape data
	with da.SearchCursor(inputFeature, "SHAPE@") as cursor:
		for row in cursor:
			outputPolygon = row[0]

			with da.InsertCursor(fc, ["SHAPE@", "AUTHOR", "TITLE", "SURV_TYPE", "SITE_COUNT", "IF_COUNT", "EL_COUNT", "ZONE", "X", "Y", "ACRES", "DATE", "CONF", "SOURCE"]) as cursor:
				cursor.insertRow([outputPolygon, reportAuthor, reportTitle, surveyType, int(siteCount), int(ifCount), int(elCount), int(zone), outputPolygon.centroid.X, outputPolygon.centroid.Y, outputPolygon.getArea("GEODESIC", "ACRES"), sDate, "HC", "Tetra Tech Inc."])
