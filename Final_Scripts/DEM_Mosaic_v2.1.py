import os, sys, datetime, time, gdal, argparse
import numpy as np

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

    # Initialize Class Attributes
	def __init__(self, dataset):
        
		self.dataset = dataset
		self.geoTransform = dataset.GetGeoTransform()
		self.projection = dataset.GetProjection()

################################################################################################################################################

	def array2raster(self, footConversion=False):

		# Isolate Raster Band
		rBand = self.dataset.GetRasterBand(1)

		# Convert dataset to numpy array
		rasterArray = np.array(rBand.ReadAsArray())

		return rasterArray * 3.28084

################################################################################################################################################
		
	def raster2array(self, array, fileName):

		# Extract necessary GeoTransformation data
		originX = self.geoTransform[0]
		originY = self.geoTransform[3]
		pixelHeight = np.abs(self.geoTransform[5])
		pixelWidth = np.abs(self.geoTransform[1])

		# Isolate Columns of Array
		cols = array.shape[1]
		rows = array.shape[0]

		# Create Driver
		driver = gdal.GetDriverByName('GTiff')
		outRaster = driver.Create(fileName, cols, rows, 1, gdal.GDT_Float32)

		outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
		rBand = outRaster.GetRasterBand(1)
		rBand.WriteArray(array)

		# Project raster
		outRaster.SetProjection(self.projection)

		# Fill Raster
		rBand.FlushCache()

"""
========================================================================
DEM_Mosaic_v2.1.py
========================================================================
Author: Mitchell Fyock
# ========================================================================
Date			Modifier	Description of Change
12/19/2017		MF			Complete rewrite of DEM Mosaic script
========================================================================
Description:
Takes an empty raster dataset and loads it with individual rasters located
in a given directory.  Converts raster from meters to feet if desired.
Creates additional Slope and Aspect rasters if desired.
"""

if __name__ == '__main__':
	
	sTime = time.time()
	
	# Initialize Parameters
	parser = argparse.ArgumentParser()
	parser.add_argument("inputFolder", type=str, help="Folder that contains DEM .Tifs or SubFolders containing .Tifs")
	parser.add_argument("outputFolder", type=str, help="Directory Location for Output Files")
	args = parser.parse_args()

	# Collect raster images
	gTiffs = getRasters(args.inputFolder)
	virtualMosaic = gdal.BuildVRT('virtualRaster.vrt', gTiffs)
	
	# Convert Temporary Mosaic to GeoTiff
	gdal.Translate(os.path.join(args.outputFolder,'DEM_Mosaic.tif'), virtualMosaic)
	
	# Process Slope and Aspect
	demSlope = gdal.DEMProcessing(os.path.join(args.outputFolder, 'DEM_Slope.tif'), virtualMosaic, "slope")
	demAspect = gdal.DEMProcessing(os.path.join(args.outputFolder, 'DEM_Aspect.tif'), virtualMosaic, "aspect")
	
	# Convert DEM Mosaic from Meters to Feet
	dem = RasterProcessor(gdal.Open(os.path.join(args.outputFolder,'DEM_Mosaic.tif')))
	demArray = dem.array2raster(footConversion=True)
	dem.raster2array(demArray, os.path.join(args.outputFolder, 'DEM_Mosaic_ft.tif'))
	
	print('{} Seconds'.format(time.time() - sTime))
