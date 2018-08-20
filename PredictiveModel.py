from arcpy import *
import numpy as np
import os, sys

# Set Environment and Check Out Extension
CheckOutExtension("Spatial")
desc = Describe(r'C:\Users\Mitchell.Fyock\Desktop\Projects\KS_Flat_Ridge_Wind_Farm\GIS\Data\TetraTech\Ks_Flat_Ridge_Wind_Farm_Master.gdb\Hydrology\NHDWaterbody')
extent = desc.extent
env.extent = extent
env.outputCoordinatSystem = desc.spatialReference

swCorner = Point(extent.XMin, extent.YMin)

stream_ds = r'C:\Users\Mitchell.Fyock\Desktop\Projects\KS_Flat_Ridge_Wind_Farm\GIS\Data\TetraTech\Ks_Flat_Ridge_Wind_Farm_Master.gdb\Hydrology\NHDFlowline'
waterbody_ds = r'C:\Users\Mitchell.Fyock\Desktop\Projects\KS_Flat_Ridge_Wind_Farm\GIS\Data\TetraTech\Ks_Flat_Ridge_Wind_Farm_Master.gdb\Hydrology\NHDWaterbody'

pStream = management.MakeFeatureLayer(stream_ds, "Streams_Perennial", "FCode = 46006")
iStream = management.MakeFeatureLayer(stream_ds, "Streams_Intermittent", "FCode = 46003")

def Write_Raster(lyr, outName):
    eucDist = sa.EucDistance(lyr, '', 30)
    arr = np.array(RasterToNumPyArray(eucDist))
    arr_ft = arr * 3.28084

    arr_copy = arr_ft.copy()

    arr_ft[np.where((arr_copy >= 0) & (arr_copy <= 250))] = 3
    arr_ft[np.where((arr_copy > 250) & (arr_copy <= 500))] = 2
    arr_ft[np.where(arr_copy > 500)] = 1

    raster = NumPyArrayToRaster(arr_ft, lower_left_corner=swCorner, x_cell_size=30, value_to_nodata=-999)
    raster.save(r'C:\Users\Mitchell.Fyock\Desktop\New folder\{}.tif'.format(outName))

    del eucDist, arr, arr_ft, raster

    return

pStreamDist = Write_Raster(pStream, "PStream")
