import arcpy, os
from arcpy import *

def layer_to_kmz(mxd, folder):
	current_mxd = mapping.MapDocument(mxd)
	layers = []
	for layer in mapping.ListLayers(current_mxd):
		layers.append(layer)
	for layer in layers:
		conversion.LayerToKML(layer, os.path.join(folder, str(layer) + ".kmz"))
		
map_document = GetParameterAsText(0)
output_location = GetParameterAsText(1)

layer_to_kmz(map_document, output_location)
