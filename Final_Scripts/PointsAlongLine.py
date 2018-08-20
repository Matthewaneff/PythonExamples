from arcpy import *
import os, sys

"""
========================================================================
PointsAlongLine.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
05/02/2017		MF			Created
========================================================================
Adds point features to existing feature class at user-defined spacing
interval
"""


'''Define Inputs'''
inputFeature = GetParameterAsText(0)
try:
	desc = Describe(inputFeature)
	desc.shapeType == 'Polyline'
except ValueError:
	AddError('Input Feature Must be Polyline')
	sys.exit()

inputLength = GetParameterAsText(1)

(value, metric) = inputLength.split(" ")

if metric.lower() == 'meters':
	length = float(value)
elif metric.lower() == 'feet':
	length = float(value) * 0.3048
else:
	AddError('Please Choose a Different Linear Unit')

outputFeature = GetParameterAsText(2)
idField = GetParameterAsText(3)

'''Create STP Points'''

with da.SearchCursor(inputFeature, 'SHAPE@') as cursor:
	for row in cursor:
		featLength = row[0].length
		count = int(featLength / 20)
		
		for i in range(count):
			num = i * length
			point = row[0].positionAlongLine(num)
			with da.InsertCursor(outputFeature, ["SHAPE@", idField]) as inscurs:
				inscurs.insertRow([point, "SPT_{}".format(i + 1)])
