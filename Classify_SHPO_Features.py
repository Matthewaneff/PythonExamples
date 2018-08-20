import os, sys, datetime
from arcpy import *
import ogr, osr, gdal
import numpy as np

def Raster2Array(raster):
	
	'''
	This function converts a raster image to a classified array
	
	~Inputs~
	
	raster: georeferenced raster image
	
	'''
	
	# Isolate a raster band and convert it to a NumPy array
	rband = raster.GetRasterBand(1)
	rArray = np.array(rband.ReadAsArray())
	
	# Reclasssify the array into two classes
	rArray[rArray < 254] = 1
	rArray[rArray >= 254] = 0
	
	return rArray

def Array2Raster(array, outputRasterName, geoTransform, projection):
	
	'''
	This function converts a NumPy array to a new raster
	
	~Inputs~
	
	array: Numpy array
	outputRasterName: file name and directory
	geoTransform: GeoTransformation of the original raster image
	projection: Projection of the original raster image
	
	'''
	
	# Collect the rows and columns from the array
	rows = array.shape[0]
	cols = array.shape[1]
	
	# Create an empty geotiff
	driver = gdal.GetDriverByName('GTiff')
	newRaster = driver.Create(outputRasterName, cols, rows, 1, gdal.GDT_UInt16)
	
	# Set the transformation
	newRaster.SetGeoTransform(geoTransform)

	# Collect the raster band to write the array to
	outBand = newRaster.GetRasterBand(1)
	outBand.WriteArray(array)
	
	# Set the new raster's projection
	newRaster.SetProjection(projection)
	
	# Flush the cache and close the file
	outBand.FlushCache()
	
	return

"""
========================================================================
Classify_SHPO_Features.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
04/20/2018  	MF			Created
========================================================================
Description:
This script is designed to automate the feature extraction process from
GeoTiffs.  It uses supervised-classification to separate pixels with RGB
values of 255,255,255 from pixels with a different value.  It then selects
the pixels without the 255,255,255 RGB value and converts them to a new
featureclasss
"""

if __name__ == '__main__':
	
	# Initialize paramters
	inputRaster = GetParameterAsText(0)
	outputWorkspace = GetParameterAsText(1)
	outputRaster = GetParameterAsText(2)
	outputRaster = os.path.join(outputWorkspace, outputRaster + '.tif')
	outputFeatureclass = GetParameterAsText(3)

	# Open the input raster
	ds = gdal.Open(inputRaster)
	
	# Convert the input raster to a classified array
	array = Raster2Array(ds)
	
	# Convert the classified array to a new raster image
	Array2Raster(array, outputRaster, ds.GetGeoTransform(), ds.GetProjection())
	
	# Create a raster attribute table for the new image
	management.BuildRasterAttributeTable(outputRaster)
	
	# Convert the new raster to a layer file, and select the cells with a value of 1
	lyr = management.MakeRasterLayer(outputRaster, "Raster_Layer")
	selection = management.SelectLayerByAttribute(lyr, "NEW_SELECTION", "Value = 1")
	
	# Convert the selected raster cells to a new featureclass
	conversion.RasterToPolygon("Raster_Layer", outputFeatureclass, "SIMPLIFY", "Value")
