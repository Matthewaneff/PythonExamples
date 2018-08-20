import os, sys, datetime
from arcpy import *

env.overwriteOutput = True

def writeLog(*argv):
	AddMessage(' ')
	AddMessage("===================================================================")
	sVersionInfo = 'Export_Project_Maps.py, v20180318'
	AddMessage('Export Project Maps, {}'.format(sVersionInfo))
	AddMessage("")
	AddMessage("Support: mitchell.fyock@tetratech.com, 303-217-3724")
	AddMessage("")
	AddMessage("Map Document: {}".format(argv[0]))
	AddMessage("Output Location: {}".format(argv[1]))
	AddMessage("===================================================================")
	AddMessage(" ")

"""
========================================================================
Export_Project_Map.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
03/07/2018		MF			Created
03/17/2018		MF			Added Output Name parameter
========================================================================
This script is designed to eliminate the tedious task of creating 
multiple maps with different basemaps and file extensions needed for
project reports.
"""

if __name__ == '__main__':
	
	# Initialize parameters
	mxd = mapping.MapDocument(GetParameterAsText(0))
	outputLocation = GetParameterAsText(1)
	outName = GetParameterAsText(2).replace(' ', '_')
	
	# Write Log
	writeLog(mxd.filePath, outputLocation)
	
	# Isolate data frame
	priFrame = mapping.ListDataFrames(mxd)[0]
	
	# Check to see if correct basemaps are in the document.  If not, force exit script
	groups = []
	for lyr in mapping.ListLayers(mxd, '', priFrame):
		if lyr.isGroupLayer:
			groups.append(lyr.name)
	
	if 'USA_Topo_Maps' not in groups and 'World Imagery' not in groups:
		AddError('ArcMap Document Does Not Contain USA Topo Maps and/or World Imagery Layers')
		AddError('Please Add Layers and Re-Run Tool')
		sys.exit()
	
	# Turn off basemap layers
	for lyr in mapping.ListLayers(mxd, '', priFrame):
		if lyr.isGroupLayer:
			lyr.visible = False
			RefreshActiveView()
	
	# Loop through layers
	for lyr in mapping.ListLayers(mxd, '', priFrame):
		
		# If layer is a group layer, perform following steps
		if lyr.isGroupLayer:
			
			# Turn layer on
			lyr.visible = True
			RefreshActiveView()
			
			# Export .PDF and .TIF with correct file name
			if lyr.name == 'USA_Topo_Maps':
				mapping.ExportToPDF(mxd, os.path.join(outputLocation, '{}_Topo.pdf'.format(outName)), resolution=200)
				mapping.ExportToTIFF(mxd, os.path.join(outputLocation, '{}_Topo.tif'.format(outName)))
				
			elif lyr.name == 'World Imagery':
				mapping.ExportToPDF(mxd, os.path.join(outputLocation, '{}_Aerial.pdf'.format(outName)), resolution=200)
				mapping.ExportToTIFF(mxd, os.path.join(outputLocation, '{}_Aerial.tif'.format(outName)))
			
			# Turn off layer
			lyr.visible = False
			RefreshActiveView()
		
