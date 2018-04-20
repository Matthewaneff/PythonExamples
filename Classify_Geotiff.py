import gdal
import numpy as np

def Raster2Array(rasterImage):

	'''
	This function converts a raster image to a classified array

	~Inputs~

	rasterImage: georeferenced raster image

	'''

	# Isolate a raster band and convert it to a NumPy array
	band = rasterImage.GetRasterBand(1)
	band = np.array(band.ReadAsArray())

	# Reclasssify the array into two classes
	rArray[rArray < 254] = 1
	rArray[rArray >= 254] = 0

	return rArray

def Array2Raster(array, outputFile, geoTransformation, spatialReference):

	'''
	This function converts a NumPy array to a new raster

	~Inputs~

	array: Numpy array
	outputFile: file name and directory
	geoTransformation: GeoTransformation of the original raster image
	spatialReference: Spatial reference of the original raster image

	'''

	# Collect the rows and columns from the array
	rows = array.shape[0]
	cols = array.shape[1]

	# Create an empty geotiff
	driver = gdal.GetDriverByName('GTiff')
	newRaster = driver.Create(outputFile, cols, rows, 1, gdal.GDT_UInt16)

	# Set the transformation
	newRaster.SetGeoTransform(geoTransformation)

	# Collect the raster band to write the array to
	outBand = newRaster.GetRasterBand(1)
	outBand.WriteArray(array)

	# Set the new raster's projection
	newRaster.SetProjection(spatialReference)

	# Flush the cache and close the file
	outBand.FlushCache()

	return

if __name__ == '__main__':

	inputRaster = '\some_raster.tif'
	outputRaster = '\a_different_raster.tif'

	ds = gdal.Open(inputRaster)

	newArray = Raster2Array(inputRaster)
	Array2Raster(newArray, outputRaster, ds.GetGeoTransform(), ds.GetProjection())
