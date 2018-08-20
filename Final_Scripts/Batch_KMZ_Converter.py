from arcpy import *
import sys, os, datetime

def makeNewFolder(rFolder, fName):
	
	'''
	Creates a new folder in a given directory with a designated name.
	Returns a string
	
	rFolder: root directory where new folder will be created
	fName: name of new folder
	'''
	
	os.mkdir(os.path.join(rFolder, fName))
	
	return os.path.join(rFolder, fName)


def formatFileName(fPath):

	'''
	Returns a formated basename

	fPath: file path to be reformatted
	'''

	# Isolate file name from extension
	name = os.path.basename(fPath).split('.')[:-1]
	cleanName = ''.join(name)

	return cleanName.replace('-','_').replace(' ', '_')

"""
========================================================================
Batch_KMZ_Converter.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
10/27/2017  	MF			Published
11/29/2017		MF			Redeveloped script as older version was significantly flawed
========================================================================
Description:
This script is designed to automate the time consuming task of converting
.KMZ or KML files to projected shapefiles.  It requires a user-provided 
(root) folder containing .KMZ or .KML files to create individual folders
for each file and then creates subfolders within the root folder.  Within
each newly created folder, the script converts the .KMZ or .KML file to
an ESRI geodatabase (GDB), and then exports the feature classes within the
GDB as projected shapefiles, using the user-provided projection.

Inputs:
- Folder where the KML/KMZ is located
- Desired spatial reference or projection for output shapefile
"""

def main():
	# Gather inputs
	inputFolder = GetParameterAsText(0)
	spatialReference = GetParameter(1)

	# Write to Log
	AddMessage('')
	AddMessage("===================================================================")
	sVersionInfo = 'Batch_KMZ_Converter.py, v20171129'
	AddMessage('Batch KMZ Converter, {}'.format(sVersionInfo))
	AddMessage("")
	AddMessage("Support: mitchell.fyock@tetratech.com, 303-2173724")
	AddMessage("")
	AddMessage("Input Folder: {}".format(inputFolder))
	AddMessage("Projection: {}".format(spatialReference.GCS.name))	
	AddMessage("===================================================================")

	kmzs = []

	# Loop through root directory to extract .KMZ and .KML files.  Add them to kmz list
	for root, dirs, files in os.walk(inputFolder):

		for item in files:
			if item.endswith('.kmz') or item.endswith('.kml'):
				kmzs.append(os.path.join(root, item))

	for kmz in kmzs:
		
		fileName = formatFileName(kmz)
		
		newFolder = makeNewFolder(root, fileName)
		
		# Convert KML/KMZ to GDB
		conversion.KMLToLayer(kmz, newFolder, fileName)
		gdb = os.path.join(newFolder, '{}.gdb'.format(fileName))
		env.workspace = gdb
		
		# Loop through the feature datasets and feature classes
		for ds in ListDatasets('', ''):
			for i in ListFeatureClasses('', '', ds):
				newFile = os.path.join(newFolder, fileName + '_' + i + '.shp')
				management.Project(os.path.join(gdb, ds, i), newFile, spatialReference)

if __name__ == '__main__':
	main()
