from arcpy import *
import os

def JPEG_PDF_Export(mxd, outputPath, outputName, topoLayer, imageryLayer):

	run = True

	while run is True:

		for lyr in mapping.ListLayers(mxd):
			if lyr.longName == '{}'.format(topoLayer):
				lyr.visible = True
			elif lyr.longName == '{}'.format(imageryLayer):
				lyr.visible = False

		RefreshActiveView()

		mapping.ExportToJPEG(mxd, os.path.join(outputPath, outputName + '_Topo.jpg'))
		mapping.ExportToPDF(mxd, os.path.join(outputPath, outputName + '_Topo.pdf'))

		for lyr in mapping.ListLayers(mxd):
			if lyr.longName == '{}'.format(topoLayer):
				lyr.visible = False
			elif lyr.longName == '{}'.format(imageryLayer):
				lyr.visible = True

		RefreshActiveView()

		mapping.ExportToJPEG(mxd, os.path.join(outputPath, outputName + '_Aerial.jpg'))
		mapping.ExportToPDF(mxd, os.path.join(outputPath, outputName + '_Aerial.pdf'))

		run = False

	return

'''
========================================================================
JPEG_PDF_Export.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
6/21/2017		MF			Created
========================================================================
This script is designed to expedite the process of exporting JPEGs and PDFs
from MXDs utilizing a user-provided ArcMap Document and a corresponding file
and folder
'''

mxd = mapping.MapDocument(GetParameterAsText(0))
outName = GetParameterAsText(1)
outPath = GetParameterAsText(2)

if __name__ == '__main__':
	JPEG_PDF_Export(mxd, outPath, outName, r'C:\Windows\system32\Basemap\USA_Topo_Maps', r'C:\Windows\system32\Basemap\World Imagery')
