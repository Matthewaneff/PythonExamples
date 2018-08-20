import os, sys, datetime
import gdal
from arcpy import *
import numpy as np

def writeLog(*argv):
	AddMessage(' ')
	AddMessage("===================================================================")
	sVersionInfo = 'ExportSitesToGDB.py, v20171208'
	AddMessage('Export Sites to Shapefiles, {}'.format(sVersionInfo))
	AddMessage("")
	AddMessage("Support: mitchell.fyock@tetratech.com, 303-217-3724")
	AddMessage("")
	AddMessage("Input Folder: {}".format(argv[0]))
	AddMessage("Output Location: {}".format(argv[1]))
	if argv[2]:
		AddMessage("Slope Map Output Included")
	if argv[3]:
		AddMessage("Aspect Map Output Included")
	AddMessage("===================================================================")
	AddMessage(" ")

################################################################################################################################################

def getRasters(dirLocation):
	
	fileList = []
	
	for tif in os.listdir(dirLocation):
		if tif.split('.')[-1] == 'tif':
			fileList.append(os.path.join(dirLocation, tif))
	
	for root, dirs, files in os.walk(dirLocation):
		for directory in dirs:
			for tif in os.listdir(os.path.join(root, directory)):
				if tif.split('.')[-1] == 'tif':
					fileList.append(os.path.join(root, directory, tif))
	
	return fileList

################################################################################################################################################

class RasterProcessor(object):
	
	def __init__(self, dataset):
		
		self.dataset = dataset
	
	def array2raster(self, footConversion=False):
		
		geoTransform = self.dataset.GetGeoTransform()
		
		# Extract necessary GeoTransformation data
		upperLeftX = geoTransform[0]
		upperLeftY = geoTransform[3]
		pixelHeight = np.abs(geoTransform[5])
		pixelWidth = np.abs(geoTransform[1])
		xPixelCount = self.dataset.RasterXSize
		yPixelCount = self.dataset.RasterYSize
		
		# Create Lower Left Point
		lowerLeftCorner = Point(upperLeftX, (upperLeftY - (pixelHeight * yPixelCount)))
		
		# Convert dataset to numpy array
		if not footConversion:
			rasterArray = np.array(self.dataset.ReadAsArray())
		else:
			rasterArray = np.array(self.dataset.ReadAsArray()) * 3.28084
		
		# Convert array to Arcpy Raster
		newRaster = NumPyArrayToRaster(rasterArray, lowerLeftCorner, pixelWidth, pixelHeight, -9999)
	
		return newRaster
		
		

"""
========================================================================
DEM_Mosaic.py
========================================================================
Author: Mitchell Fyock
# ========================================================================
Date			Modifier	Description of Change
NA      		MF			Created
08/31/2017      MF          Added script description
10/27/2017      MF          Added Log
========================================================================
Description:
Takes an empty raster dataset and loads it with individual rasters located
in a given directory.  Converts raster from meters to feet if desired.
Creates additional Slope and Aspect rasters if desired.

Inputs:
- folder: folder that contains raster images
- raster_dataset: empty raster dataset to be filled
- imperialConversion: (boolean) converts from meters to feet
- additionalRasters: (boolean) creates Slope and Aspect rasters
"""

if __name__ == '__main__':
	
	inputFolder = GetParameterAsText(0)
	gdb = GetParameterAsText(1)
	addSlope = GetParameter(2)
	addAspect = GetParameter(3)

	writeLog(inputFolder, gdb, addSlope, addAspect)

	# Collect raster images
	gTiffs = getRasters(inputFolder)
	virtualMosaic = gdal.BuildVRT('virtualRaster.vrt', gTiffs)
	
	# Process DEM Mosaic
	tempDEM = RasterProcessor(virtualMosaic)
	mDEM = tempDEM.array2raster()
	mDEM.save(os.path.join(gdb, 'DEM_Mosaic'))
	del mDEM, tempDEM
	
	tempDEM = RasterProcessor(virtualMosaic)
	ftDEM = tempDEM.array2raster(footConversion=True)
	ftDEM.save(os.path.join(gdb, 'DEM_Mosaic_ft'))
	del ftDEM, tempDEM

	if addSlope:
		demSlope = gdal.DEMProcessing('slope.vrt', mosaic, "slope")
		tempSlope = RasterProcessor(demSlope)
		outSlope = tempSlope.array2raster()
		outSlope.save(os.path.join(gdb, 'DEM_Slope'))
		
	if addAspect:
		demAspect = gdal.DEMProcessing('aspec.vrt', mosaic, "aspect")
		tempAspect = RasterProcessor(demAspect)
		outAspect = tempAspect.array2raster()
		outAspect.save(os.path.join(gdb, 'DEM_Aspect'))
