import os, sys, datetime
from arcpy import *

def writeLog(*argv):
	AddMessage(' ')
	AddMessage("===================================================================")
	sVersionInfo = 'ExportSitesToGDB.py, v20171208'
	AddMessage('Export Sites to Shapefiles, {}'.format(sVersionInfo))
	AddMessage("")
	AddMessage("Support: mitchell.fyock@tetratech.com, 303-217-3724")
	AddMessage("")
	AddMessage("Input Feature: {}".format(argv[0]))
	AddMessage("ID Field: '{}'".format(argv[1]))
	AddMessage("Output Location: {}".format(argv[2]))
	AddMessage("Delete Fields: {}".format(str(argv[3])))
	AddMessage("===================================================================")
	AddMessage(" ")

########################################################################

class inputDataset(object):
	
	def __init__(self, featureClass):
	
		self.featureClass = featureClass
		
		self.lyr = management.MakeFeatureLayer(featureClass, "featureClass")

########################################################################

	def getFileNames(self, nameField):
		
		nameList = []
		
		with da.SearchCursor(self.featureClass, nameField) as cursor:
			for row in cursor:
				
				nameList.append(str(row[0]))
				
		return nameList
	
########################################################################

	def SelectAndExport(self, outputLocation, fID, nameField):
		
		fName = fID.replace(' ', '_')
		
		if fName[0].isalpha():
			conversion.FeatureClassToFeatureClass(self.lyr, outputLocation, fName, "{} = '{}'".format(nameField, fID))
		
		else:
			conversion.FeatureClassToFeatureClass(self.lyr, outputLocation, '_' + fName, "{} = '{}'".format(nameField, fID))

########################################################################

	def DeleteFields(self, outputLocation, nameField):
		
		env.workspace = outputLocation
		
		for fc in ListFeatureClasses():
			
			fields = [str(i.name) for i in ListFields(fc) if str(i.name) not in [nameField, 'Shape_Length', 'Shape_Area', 'OBJECTID', 'Shape', 'FID']]
			
			management.DeleteField(fc, fields)

########################################################################

"""
========================================================================
ExportSiteToGDB.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
12/08/2017		MF			Created
========================================================================

"""


if __name__ == '__main__':
	
	# Gather inputs | Create a instance of the inputDataset class
	inputFeatureClass = inputDataset(GetParameterAsText(0))
	inputField = GetParameterAsText(1)
	outputGDB = GetParameterAsText(2)
	delFields = GetParameter(3)
	
	# Write to log
	writeLog(inputFeatureClass.featureClass, inputField, outputGDB, delFields)
	
	# Create a list of all the separate sites in the input feature class
	sites = inputFeatureClass.getFileNames(inputField)
	
	# loop through 'sites' list, exporting each feature to output location
	for i in sites:
		inputFeatureClass.SelectAndExport(outputGDB, i, inputField)
	
	# If 'delFields' is True, delete all fields except ID
	if delFields == True:
		inputFeatureClass.DeleteFields(outputGDB, inputField)
