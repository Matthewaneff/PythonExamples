from arcpy import *
import os, sys
import pandas as pd

env.overwriteOutput = True
CheckOutExtension('Spatial')

nhdWaterbody = GetParameterAsText(0)
nhdStream = GetParameterAsText(1)
slope = GetParameterAsText(2)
veg = GetParameterAsText(3)
USFWS_Wetlands = GetParameterAsText(4)
GAP_Reclass_Table = GetParameterAsText(5)
fromCol = GetParameterAsText(6)
toCol = GetParameterAsText(7)
outputGDB = GetParameterAsText(8)

df = pd.DataFrame(pd.read_csv(GAP_Reclass_Table))
remapValues = []
for i in range(len(df)):
	remapValues.append([df['{}'.format(fromCol)].iloc[i], df['{}'.format(toCol)].iloc[i]])

# Isolate Features
nhd_Pond = management.MakeFeatureLayer(nhdWaterbody, "NHD_Waterbody", "FType = 390")
pStream = management.MakeFeatureLayer(nhdStream, "Streams_Perennial", "FCode = 46006")
iStream = management.MakeFeatureLayer(nhdStream, "Streams_Intermittent", "FCode = 46003")
usfws_Pond = management.MakeFeatureLayer(USFWS_Wetlands, "USFW_Ponds", "WETLAND_TYPE IN ('Freshwater Pond', 'Lake')")

# Merge and Dissolve USGS NHD waterbody datatset with USFWS waterbody dataset
pond_merge = management.Merge([nhd_Pond, usfws_Pond], "in_memory/merge")
pond_dissolve = management.Dissolve(pond_merge, "in_memory/dissolve")

# Create Euclidean Distance Rasters for water features
AddMessage('Creating Euclidean Distance Models...')
pStream_ed = sa.EucDistance(pStream, '', 30) *  3.28084
iStream_ed = sa.EucDistance(iStream, '', 30) * 3.28084
Waterbody_ed = sa.EucDistance(pond_dissolve, '', 30) * 3.28084

# Reclassify Rasters
AddMessage("Reclassifying Rasters...")
dist_to_water_range = sa.RemapRange([[0, 50, 2], [50, 250, 3], [250, 500, 2], [500, 100000, 0]])

pStream_Reclass = sa.Reclassify(pStream_ed, 'Value', dist_to_water_range)
iStream_Reclass = sa.Reclassify(iStream_ed, 'Value', dist_to_water_range)
waterbody_reclass = sa.Reclassify(Waterbody_ed, 'Value', dist_to_water_range)

slope_range = sa.RemapRange([[0, 30, 3], [30, 90, 0]])
slope_Reclass = sa.Reclassify(slope, 'Value', slope_range)

veg_values = sa.RemapValue(remapValues)
veg_Reclass = sa.Reclassify(veg, 'Value', veg_values)

# Combine and export Rasters
AddMessage('Generating Final Image...')
mapAlgebra = sa.Int((pStream_Reclass * 0.4) + (waterbody_reclass * 0.1) + (iStream_Reclass * 0.2) + (slope_Reclass * 0.1) + (veg_Reclass * 0.2))

mapAlgebra.save(os.path.join(outputGDB, 'Predictive_Model'))
