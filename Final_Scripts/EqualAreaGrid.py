import os, sys, datetime
from arcpy import *
import numpy as np

def ConvertUnit(inValue, inUnit, fcUnit):
	
	if inUnit == 'acres' and fcUnit == 'meter':
		return inValue * 4046.86
	
	elif inUnit == 'squaremeters' and fcUnit == 'meter':
		return inValue
	
	elif inUnit == 'squarekilometers' and fcUnit == 'meter':
		return inValue * 1000000
	
	elif inUnit =='squarefeet' and fcUnit == 'meter':
		return inValue * 0.09290304
		
	elif inUnit == 'squaremiles' and fcUnit == 'meter':
		return inValue * 2589975.24
	
	elif inUnit == 'acres' and fcUnit in ['foot', 'foot_us']:
		return inValue * 43560

	elif inUnit == 'squaremeters' and fcUnit in ['foot', 'foot_us']:
		return inValue * 10.7639111056

	elif inUnit == 'squarekilometers' and fcUnit in ['foot', 'foot_us']:
		return inValue * 10763911.1056

	elif inUnit == 'squaremiles' and fcUnit in ['foot', 'foot_us']:
		return inValue * 27878400
	
#####################################################################################

class SquareGrid(object):
	
	def __init__(self, feature, squareSide):
		
		self.feature = feature
		self.squareSide = squareSide

#####################################################################################
		
	def getNWCorner(self):
		
		extent = Describe(self.feature).extent
		
		return extent.XMin, extent.YMax

#####################################################################################
	
	def getInterval(self):
		
		extent = Describe(self.feature).extent
		
		xRange = extent.XMax - extent.XMin
		yRange = extent.YMax - extent.YMin
		
		return np.ceil(xRange / self.squareSide), np.ceil(yRange / self.squareSide)

#####################################################################################
	
	def getGrid(self, gridInterval, NWCorner):
		
		nwX = NWCorner[0]
		nwY = NWCorner[1]
		
		xInt = gridInterval[0]
		yInt = gridInterval[1]
		
		coordinateList = []
		
		for x in range(int(xInt)):
			for y in range(int(yInt)):
				
				X = nwX + (x * self.squareSide)
				Y = nwY - (y * self.squareSide)
				
				coordinateList.append([X, Y])
		
		return coordinateList

#####################################################################################

	def createSquare(self, coordinatePair, array):
		
		nwX = coordinatePair[0]
		nwY = coordinatePair[1]
		
		arr = Array()
		
		arr.append(Point(nwX, nwY))
		arr.append(Point((nwX + self.squareSide), nwY))
		arr.append(Point((nwX + self.squareSide), (nwY - self.squareSide)))
		arr.append(Point(nwX, (nwY - self.squareSide)))
		
		array.add(arr)
		
		return

"""
========================================================================
EqualAreaSquareGrid.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
12/01/2017		MF			Created
========================================================================
Uses the spatial extent of the input feature to create a grid of equal-area
squares and export them as a polygon featureclass or polyline featureclass
"""

if __name__ == '__main__':
	env.overwriteOutput = True

	'''Gather Inputs'''
	inputFeature = GetParameterAsText(0)
	desc = Describe(inputFeature)

	(area, unit) = GetParameterAsText(1).split(' ')

	outputFeature = GetParameterAsText(2)
	(outputFolder, outputName) = os.path.split(outputFeature)
	
	# Perform file name manipulation, if necessary
	if Describe(outputFolder).workspaceType == 'FileSystem':
		if outputName.split('.')[-1] != 'shp':
			outputName == str(outputName + '.shp')
			outputFeature = str(outputFeature + '.shp')

	makePolyline = GetParameter(3)

	# Write to Log
	AddMessage('')
	AddMessage("===================================================================")
	sVersionInfo = 'EqualAreaGrid.py, v20171204'
	AddMessage('Equal Area Grid Generator, {}'.format(sVersionInfo))
	AddMessage("")
	AddMessage("Support: mitchell.fyock@tetratech.com, 303-2173724")
	AddMessage("")
	AddMessage("Input Feature: {}".format(inputFolder))
	AddMessage("Output Feature: {}".format(outputFeature))
	AddMessage("===================================================================")
	
	# Create empty feature class
	if makePolyline == True:
		management.CreateFeatureclass(outputFolder, outputName, 'POLYLINE', '', '', '', desc.spatialReference)

	else:
		management.CreateFeatureclass(outputFolder, outputName, 'POLYGON', '', '', '', desc.spatialReference)
		
	'''Begin Script'''

	sideLength = np.sqrt(ConvertUnit(float(area), unit.lower(), desc.spatialReference.linearUnitName.lower()))

	fc = SquareGrid(inputFeature, sideLength)

	fArray = Array()

	fcNWC = fc.getNWCorner()
	fcINT = fc.getInterval()
	grid = fc.getGrid(fcINT, fcNWC)

	for coordPair in grid:
		fc.createSquare(coordPair, fArray)

	with da.InsertCursor(outputFeature, "SHAPE@") as cursor:
		for shape in fArray:
	
			if makePolyline == True:
				cursor.insertRow([Polyline(shape)])
			else:
				cursor.insertRow([Polygon(shape)])

