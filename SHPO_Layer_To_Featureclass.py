import os, sys, datetime
from arcpy import *
import numpy as np
import gdal, ogr, osr

class RasterProcessor(object):
	
	def __init__(self, ds):
		self.ds = ds
		self.projection = ds.GetProjection()
		self.transform = ds.GetGeoTransform()
	
	def processArray(self):
		
		array = np.array(self.ds.GetRasterBand(1).ReadAsArray())
		
		array[np.where((array != 254) & (array != 0))] = 2
		array[np.where(array == 254)] = 1

		return array
	
	def array2Raster(self, nArray, rasterPath):
		rows = nArray.shape[0]
		cols = nArray.shape[1]
		
		# Create Empty Raster
		driver = gdal.GetDriverByName('GTiff')
		raster = driver.Create(rasterPath, cols, rows, 1, gdal.GDT_UInt16)
		
		# Handle geotransformations
		raster.SetGeoTransform(self.transform)
		
		# Write array to raster band
		outBand = raster.GetRasterBand(1)
		outBand.WriteArray(nArray)
		
		# Set Spatial Reference
		outSR = osr.SpatialReference()
		outSR.ImportFromWkt(self.projection)
		raster.SetProjection(outSR.ExportToWkt())
		
		# Flush Cache
		outBand.FlushCache()

if __name__ == '__main__':
	
	# Initialize parameters
	inputRaster = GetParameterAsText(0)
	outputRaster = GetParameterAsText(1)
	outputFC = GetParameterAsText(2)
	
	# Create Instance of RasterProcessor
	geoTiff = RasterProcessor(gdal.Open(inputRaster))
	
	# Create array from raster processer
	rasterArray = geoTiff.processArray()
	
	# Write array to output raster
	geoTiff.array2Raster(rasterArray, outputRaster)
	
	
