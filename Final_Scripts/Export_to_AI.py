import os
from arcpy import *

def writeLog(*argv):
	AddMessage(' ')
	AddMessage("===================================================================")
	sVersionInfo = 'Export_to_AI.py, v20180302'
	AddMessage('Export Layers to .AI, {}'.format(sVersionInfo))
	AddMessage("")
	AddMessage("Support: mitchell.fyock@tetratech.com, 303-217-3724")
	AddMessage("")
	AddMessage("Input MXD: {}".format(argv[0]))
	AddMessage("Output Location: {}".format(argv[1]))
	AddMessage("===================================================================")
	AddMessage(" ")


if __name__ == '__main__':
	
	# Initialize Parameters
	mxd = mapping.MapDocument(GetParameterAsText(0))
	outputLocation = GetParameterAsText(1)
	
	# Write to log
	writeLog(mxd.filepath, outputLocation)
	
	# Identify layers in MXD
	layers = mapping.ListLayers(mxd)
	
	# Ensure that all layers are off
	for layer in layers:
		layer.visible = False
	
	RefreshActiveView()

	# Loop through Layers list to turn each layer on, export it as a .AI file, and turn it off
	for layer in layers:
		layer.visible = True
		RefreshActiveView()
		
		mapping.ExportToAI(mxd, os.path.join(outputLocation, '{}.ai'.format(layer.name)))
		
		layer.visible = False
		RefreshActiveView()
	
