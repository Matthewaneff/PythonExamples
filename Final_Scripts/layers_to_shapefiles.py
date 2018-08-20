import arcpy
from arcpy import *

def layer_to_shape(mxd, folder):
	current_map = mapping.MapDocument(mxd)
	layers = []
	for layer in mapping.ListLayers(current_map):
		layers.append(layer)
	for layer in layers:
		conversion.FeatureClassToShapefile(layer.name, folder)

map_document = GetParameterAsText(0)
output_location = GetParameterAsText(1)

layer_to_shape(map_document, output_location)
