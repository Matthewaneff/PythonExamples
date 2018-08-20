from arcpy import *
import os, sys

def new_multipart(inFeat, outFeat):
	
	'''
	This function uses a Search Cursor to gather the geometry from
	the inFeat object and insert them into the outFeat object using
	an Insert Cursor
	'''
	
	with da.SearchCursor(inFeat, "SHAPE@") as cursor:
		for row in cursor:
			count = row[0].partCount
			array = Array()
			
			for i in range(count):
				part = Array()
				
				for vertice in row[0].getPart(i):
					point = Point(vertice.X, vertice.Y)
					part.append(point)
			
				array.add(part)
			
			with da.InsertCursor(outFeat, "SHAPE@") as inscurs:
				
				if desc.shapeType == 'Polygon':
					inscurs.insertRow([Polygon(array)])
				
				elif desc.shapeType == 'Polyline':
					inscurs.insertRow([Polyline(array)])
				
				elif desc.shapeType == 'Point':
					inscurs.insertRow([PointGeometry(array)])
				
				elif desc.shapeType == 'Multipoint':
					inscurs.insertRow([Multipoint(array)])
				
				else:
					AddError('Output Feature type Not Recognized')
					sys.exit()

"""
========================================================================
MultipartFeature.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
05/02/2017		MF			Created
========================================================================
This script is meant to be used as a template for future scripts that
which include feature classes that contain multipart features
"""

# Gather Input Paramters
inputFeature = GetParameterAsText(0)

desc = Describe(inputFeature)
shapeType = desc.shapeType
spaRef = desc.spatialReference

outputFeature = GetParameterAsText(1)
(folder, file) = os.path.split(outputFeature)

newFeature = management.CreateFeatureclass(folder, file, '{}'.format(shapeType.upper()), '', '', '', spaRef)


# Script Starts Here
if __name__ == '__main__':
	new_multipart(inputFeature, newFeature)
