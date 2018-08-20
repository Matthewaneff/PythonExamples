import os, sys, datetime
from arcpy import *

def writeLog(*argv):
	AddMessage(' ')
	AddMessage("===================================================================")
	sVersionInfo = 'Create_Rectangle_From_Feature.py, v20180308'
	AddMessage('Create Rectangle From Feature, {}'.format(sVersionInfo))
	AddMessage("")
	AddMessage("Support: mitchell.fyock@tetratech.com, 303-217-3724")
	AddMessage("")
	AddMessage("Input Layers: {}".format(argv[0]))
	AddMessage("Output Location: {}".format(argv[1]))
	AddMessage("===================================================================")
	AddMessage(" ")

"""
========================================================================
Export_Layer_To_KMZ.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
04/06/2018		MF			Created
========================================================================
Simple export tool that converts feature layers to .KMZs in a user
specified folder
"""

inputLayers = GetParameter(0)
outputLocation = GetParameterAsText(1)

for item in inputLayers:
	conversion.LayerToKML(item, os.path.join(outputLocation, item.name + '.kmz'))
