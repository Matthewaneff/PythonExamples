from arcpy import *
import os, sys

env.overwriteOutput = "True"

"""
========================================================================
Tech_Report_Chapter7
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
01/04/2017		MF			Created
========================================================================
This script is designed to create a basic, standardized project folder
with a geodatabase that contains all feature datasets, feature classes,
and domains required.
"""

input_feature = GetParameter(0)
input_field = GetParameterAsText(1)
(output_folder, output_feature) = os.path.split(GetParameterAsText(2))
env.workspace = output_folder


domains = ['Landuse', 'SurfaceVis', 'ArchPot', 'ShovProb']
desc = Describe(input_feature)
spatialRef  = desc.spatialReference

# Gather geometry and name from input feature class
pointLst = []
siteLst = []
with da.SearchCursor(input_feature, ["SHAPE@XY", input_field]) as cursor:
	for row in cursor:
		array = Array()
		(x,y) = row[0]							# Split geometry into x and y
		array.append(Point(x,y))				# add new point to array
		pointLst.append(array)					# add array to pointLst
		siteLst.append(row[1])					# add name to siteLst


# Create Empty Feature and Add Necessary Fields
fc = management.CreateFeatureclass(output_folder, output_feature, "POINT", '','','', spatialRef)
fields = ['TurbineID', 'Landuse', 'SurfaceVis', 'ArchPot', 'ShovProb', 'Comment']
[management.AddField(fc, i, "TEXT") for i in fields]

# Insert new rows into the output feature
cursor = da.InsertCursor(fc, ["SHAPE@XY", "TurbineID"])

for i in range(len(pointLst)):
	site = siteLst[i]
	coord = pointLst[i][0]
	cursor.insertRow([coord, site])

del cursor

# Assign domains to corresponding fields
domain_fields = ['Landuse', 'SurfaceVis', 'ArchPot', 'ShovProb']
for i in range(len(domain_fields)):
	domain = domains[i]
	domain_field = domain_fields[i]
	management.AssignDomainToField(output_feature, domain_field, domain)
