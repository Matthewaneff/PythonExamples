from arcpy import *
import pandas as pd
import os



wetPoly = [r'Q:\Flat Ridge\GIS\FlatRidge_IV_2018_Survey\Wetland_Polygons_ALL_180725.shp', "Wetland_Poly"]
wetPoint = [r'Q:\Flat Ridge\GIS\FlatRidge_IV_2018_Survey\Wetland_Points_ALL_171107.shp', "Wetland_Point"]
#~ permAccess = [r'C:\Users\Mitchell.Fyock\Desktop\Projects\KS_Flat_Ridge_Wind_Farm\GIS\Data\TetraTech\FR4_Impacts_20180731\CurrentLayout\Buffers\Dissolve\AccessRoads_20180518_PermBuffer_Dissolve.shp', "Access_Perm"]
#~ permAltTurbine = [r'C:\Users\Mitchell.Fyock\Desktop\Projects\KS_Flat_Ridge_Wind_Farm\GIS\Data\TetraTech\FR4_Impacts_20180731\CurrentLayout\Buffers\Dissolve\AlternateTurbines_20180518_PermBuffer_Dissolve.shp', "Alt_Turbine_Perm"]
#~ permTurbine = [r'C:\Users\Mitchell.Fyock\Desktop\Projects\KS_Flat_Ridge_Wind_Farm\GIS\Data\TetraTech\FR4_Impacts_20180731\CurrentLayout\Buffers\Dissolve\ProposedTurbines_20180518_PermBuffer_Dissolve.shp', "Turbine_Perm"]
#~ tempAccess = [r'C:\Users\Mitchell.Fyock\Desktop\Projects\KS_Flat_Ridge_Wind_Farm\GIS\Data\TetraTech\FR4_Impacts_20180731\CurrentLayout\Buffers\Dissolve\AccessRoads_20180518_TempBuffer_Dissolve.shp', "Access_Temp"]
#~ tempAltTurbine = [r'C:\Users\Mitchell.Fyock\Desktop\Projects\KS_Flat_Ridge_Wind_Farm\GIS\Data\TetraTech\FR4_Impacts_20180731\CurrentLayout\Buffers\Dissolve\AlternateTurbines_20180518_TempBuffer_Dissolve.shp', "Alt_Turbine_Temp"]
#~ tempTurbine = [r'C:\Users\Mitchell.Fyock\Desktop\Projects\KS_Flat_Ridge_Wind_Farm\GIS\Data\TetraTech\FR4_Impacts_20180731\CurrentLayout\Buffers\Dissolve\ProposedTurbines_20180518_PermBuffer_Dissolve.shp', "Turbine_Perm"]
#~ tempCrane = [r'C:\Users\Mitchell.Fyock\Desktop\Projects\KS_Flat_Ridge_Wind_Farm\GIS\Data\TetraTech\FR4_Impacts_20180731\CurrentLayout\Buffers\Dissolve\CraneWalks_20180518_TempBuffer_Dissolve.shp', "Temp_Crane_Walk"]

parcels = [r'C:\Users\Mitchell.Fyock\Desktop\Projects\KS_Flat_Ridge_Wind_Farm\GIS\Data\Consult\Parcels.shp', "Parcels"]

wetland_layers = [management.MakeFeatureLayer(item[0], item[1]) for item in [wetPoly, wetPoint]]
#~ feature_layers = [management.MakeFeatureLayer(item[0], item[1]) for item in [permAccess, permAltTurbine, permTurbine, tempAccess, tempAltTurbine, tempTurbine, tempCrane]]
land_layers = [management.MakeFeatureLayer(item[0], item[1]) for item in [parcels]]

output = []

for wetland in wetland_layers:
	with da.SearchCursor(wetland, ["FID", "Feature_ID"]) as cursor:
		sites = [[row[0], row[1]] for row in cursor]
	
	for site in sites:
		management.SelectLayerByAttribute(wetland, "NEW_SELECTION", '"FID" = {}'.format(site[0]))
		management.SelectLayerByLocation(parcels[1], "INTERSECT", wetland)
		
		p = []
		with da.SearchCursor(parcels[1], "NAME") as cursor:
			for row in cursor:
				p.append(row[0])
		
		output.append("{}|{}".format(site[1], ', '.join(p)))

with open(r'C:\Users\Mitchell.Fyock\Desktop\Projects\KS_Flat_Ridge_Wind_Farm\GIS\Data\Consult\Parcels.txt', 'w') as f:
	for row in output:
		f.write(row + "\n")
