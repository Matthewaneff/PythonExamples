import os, sys, datetime
from arcpy import *
env.overwriteOutput = True

def bufferFeature(inputFeatures, featureBuffer):

	buffers = []

	for item in inputFeatures:
		tempFeature = analysis.Buffer(item, Geometry(), featureBuffer)
		proj = row[0].projectAs(projection)
		buffers.append(proj)

	rowBuffer = buffers[0]

	for geo in buffers:
		rowBuffer = rowBuffer.union(geo)

	return rowBuffer

def point2square(inputFeatures, featureBuffer):

	buffers = []

	for item in inputFeatures:
		tempFeature = analysis.Buffer(item, Geometry(), featureBuffer)
		for feature in tempFeature:
			proj = feature.projectAs(projection)
			extent = proj.extent

			array = Array()

			array.append(Point(extent.XMin, extent.YMin))
			array.append(Point(extent.XMax, extent.YMin))
			array.append(Point(extent.XMax, extent.YMax))
			array.append(Point(extent.XMin, extent.YMax))

			buffers.append(Polygon(array))

	rowBuffer = buffers[0]

	for geo in buffers:
		rowBuffer = rowBuffer.union(geo)

	return rowBuffer

"""
========================================================================
Create_Wind_Farm_Footprint.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
04/27/2018		MF			Created
========================================================================
Creates the footprint for a project
"""

if __name__ == '__main__':

	accessRoad = GetParameterAsText(0)
	accessBuffer = GetParameterAsText(1)
	collectionLine = GetParameterAsText(2)
	collectionBuffer = GetParameterAsText(3)
	transmissionLine = GetParameterAsText(4)
	transmissionBuffer = GetParameterAsText(5)
	turbineArray = GetParameterAsText(6)
	turbineBuffer = GetParameterAsText(7)
	previousSurvey = GetParameterAsText(8)
	outputFeature = GetParameterAsText(9)
	projection = GetParameterAsText(10)

	geometryObjects = []

	if accessRoad != '' and accessBuffer != '':
		access = bufferFeature(accessRoad.split(';'), accessBuffer)
		geometryObjects.append(access)

	if collectionLine != '' and collectionBuffer != '':
		collectors = bufferFeature(collectionLine.split(';'), collectionBuffer)
		geometryObjects.append(collectors)

	if transmissionLine != '' and transmissionBuffer != '':
		transmission = bufferFeature(transmissionLine.split(';'), transmissionBuffer)
		geometryObjects.append(transmission)

	if turbineArray != '' and turbineBuffer != '':
		turbines = point2square(turbineArray.split(';'), turbineBuffer)
		geometryObjects.append(turbines)
	
	merge = management.Merge(geometryObjects, Geometry())

	if previousSurvey != '':
		dissolve = management.Dissolve(merge, Geometry())
		analysis.Erase(dissolve, outputFeature)
		
	else:
		management.Dissolve(merge, outputFeature)
