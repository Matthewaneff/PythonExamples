from arcpy import *
env.overwriteOutput = True

"""
========================================================================
Slope Analysis
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
03/07/2017		MF			Created
========================================================================
This script is designed to automate the slope analysis process.  It takes
a DEM or DEM mosaic and reclassifies it with user-provided degree, then
converts that to a shapefile.
"""


# Define inputs
dem = GetParameter(0) # User provided Digital Elevation Model Slope raster
d  = GetParameterAsText(1) # User provided threshold slope
output = GetParameter(2) # User provided output file

# Set the range and values for the reclassification process
try:
	int(d)
except ValueError:
	AddError('Degree field must be Integer')

degree = int(d)
reclass_range = sa.RemapRange([[0, degree, 1], [degree, 90, 2]])

# Perform the reclassification process on the DEM using the defined range
reclass = sa.Reclassify(dem, 'Value', reclass_range)
management.MakeRasterLayer(reclass, "DEM_Reclass")

# Perform a query on the Feature Layer to select the cells greater than
# the slope threshold
selection = management.SelectLayerByAttribute("DEM_Reclass", "NEW_SELECTION", "value = 2")

# Convert to a shapefile
conversion.RasterToPolygon(selection, output, "NO_SIMPLIFY", "VALUE")
