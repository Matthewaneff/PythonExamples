import os, sys
from arcpy import *
import pandas as pd

env.overwriteOutput = True

def writeLog(*argv):
	AddMessage(' ')
	AddMessage("===================================================================")
	sVersionInfo = 'Site_Attribute_Extraction_2.1.py, v20171215'
	AddMessage('Cultural Resource Site Attribute Extractor, {}'.format(sVersionInfo))
	AddMessage("")
	AddMessage("Support: mitchell.fyock@tetratech.com, 303-217-3724")
	AddMessage("")
	AddMessage("Input Feature: {}".format(argv[0]))
	AddMessage("ID Field: '{}'".format(argv[1]))
	AddMessage("Output Location: {}".format(argv[2]))
	AddMessage("===================================================================")
	AddMessage(" ")

class inputDataset(object):
	
	def __init__(self, feature):
		
		self.feature = feature
		self.desc = Describe(feature)

################################################################################################################################################

	def createNewFeatureClass(self, outputFeatureClass):
		
		(outputPath, outputName) = os.path.split(outputFeatureClass)
		
		newFC = management.CreateFeatureclass(outputPath, outputName, self.desc.shapeType, '', '', '', self.desc.spatialReference)
		
		return newFC

'''##########################################################################################################################################'''

class outputDataset(object):
	
	def __init__(self, feature):
		
		self.feature = feature
		self.desc = Describe(feature)

################################################################################################################################################
		
	def addFields(self, **kwargs):
		
		'''
		Adds fields to feature class
		
		kwargs:
		"textFields" = fields with a text data type
		"numFields" = fields with a double data type
		'''
		
		for field in textFields:
			
			management.AddField(self.feature, field, "TEXT")
			
		for field in numFields:
			
			management.AddField(self.feature, field, "DOUBLE")
		
		return

################################################################################################################################################
	
	def addPrimaryAttributes(self, *args):
		
		'''
		Collects basic attributes from input featureclass
		
		Args:
		args[0] = featureclass
		args[1] = featureclass ID field
		'''
		
		if self.desc.shapeType == 'Polygon':
			
			with da.InsertCursor(self.feature, ["SHAPE@", "SITE_ID", "NORTHING_m", "EASTING_m", "ACRES"]) as inscurs:
				
				with da.SearchCursor(args[0], ["SHAPE@", args[1]]) as cursor:
					for row in cursor:
						
						inscurs.insertRow([row[0], row[1], row[0].centroid.Y, row[0].centroid.X, row[0].getArea("PLANAR", "ACRES")])
		
		elif self.desc.shapeType == 'Point':
			
			with da.InsertCursor(self.feature, ["SHAPE@", "SITE_ID", "NORTHING_m", "EASTING_m"]) as inscurs:

				with da.SearchCursor(args[0], ["SHAPE@", args[1]]) as cursor:
					for row in cursor:
						
						inscurs.insertRow([row[0], row[1], row[0].centroid.X, row[0].centroid.Y])
						
################################################################################################################################################

	def collectUIDs(self):
		
		'''
		Collect the Unique Site IDs from the input Featureclass
		'''
		
		uID_List = []
		
		with da.SearchCursor(self.feature, "SITE_ID") as cursor:
			for row in cursor:
				
				uID_List.append(str(row[0]))
		
		return uID_List
		
################################################################################################################################################

	def extractJoinAttributes(self, UID_List, updateField, joinFeature, joinField):
		
		'''
		Performs Spatial Join between input Featureclass and attribute Featureclass.
		Extracts desired attribute values from attribute Featureclass and assigns them
		to input Featureclass
		'''
		
		# Perform Spatial Join
		spatialJoin = analysis.SpatialJoin(self.feature, joinFeature, "in_memory/join", "JOIN_ONE_TO_MANY", "KEEP_COMMON")
		
		# Create List to Hold Attribute Dictionaries
		ea_DictList = []
		
		# Loop Through Unique ID Values
		for d in UID_List:
			
			# Create Dictionary that Holds Unique ID
			ea_Dict = {"SITE_ID":d,}
			
			attributes = []
			
			# Use Search Cursor to Identify Attribute values assigned to Unique IDs and add them to Dictionary
			with da.SearchCursor(spatialJoin, ["SITE_ID", joinField]) as cursor:
				for row in cursor:
					if row[0] == d:
						attributes.append(row[1])
			
			# Concatenate Attribute Values If More Than One
			ea_Dict["Attributes"] = ', '.join(attributes)
			
			ea_DictList.append(ea_Dict)
		
		# Use Update Cursor to Assign attribute Featureclass values to input Featureclass rows from the Dictionary
		with da.UpdateCursor(self.feature, ['SITE_ID', updateField]) as cursor:
			for row in cursor:
				for dictionary in ea_DictList:
				
					if row[0] == dictionary['SITE_ID']:
						row[1] = dictionary['Attributes']
					
						cursor.updateRow(row)
		
		management.Delete(spatialJoin)
		
		return

################################################################################################################################################

	def extractQuadAttributes(self, UID_List, joinFeature, quadName, quadDate=False):
		
		# Perform Spatial Join
		spatialJoin = analysis.SpatialJoin(self.feature, joinFeature, "in_memory/join", "JOIN_ONE_TO_MANY", "KEEP_COMMON")
		
		# Create List to Hold Attribute Dictionaries
		ea_DictList = []
		
		# Loop Through Unique ID Values
		for d in UID_List:
			
			# Create Dictionary that Holds Unique ID
			ea_Dict = {"SITE_ID":d,}
			
			attributes = []
			
			if quadDate:
				
				with da.SearchCursor(spatialJoin, ["SITE_ID", quadName, quadDate]) as cursor:
					for row in cursor:
						if row[0] == d:
							quadrangle = "{} {}".format(row[1], str(int(row[2])))
							attributes.append(quadrangle)
			
			else:
				
				with da.SearchCursor(spatialJoin, ["SITE_ID", quadName]) as cursor:
					for row in cursor:
						if row[0] == d:
							attributes.append(row[1])

			# Concatenate Attribute Values If More Than One
			ea_Dict["Attributes"] = ', '.join(attributes)
			
			ea_DictList.append(ea_Dict)		
		
		# Use Update Cursor to Assign attribute Featureclass values to input Featureclass rows from the Dictionary
		with da.UpdateCursor(self.feature, ['SITE_ID', 'Quad']) as cursor:
			for row in cursor:
				for dictionary in ea_DictList:
				
					if row[0] == dictionary['SITE_ID']:
						row[1] = dictionary['Attributes']
					
						cursor.updateRow(row)
		
		management.Delete(spatialJoin)
		
		return

################################################################################################################################################

	def extractNearAttributes(self, updateField, joinFeature, joinField):
		
		analysis.Near(self.feature, joinFeature, '', 'NO_LOCATION', '', 'GEODESIC')
		
		UID_List = []
		
		# Identify unique Feature IDs and add them to the UID_List
		with da.SearchCursor(self.feature, "NEAR_FID") as cursor:
			for row in cursor:
				if row[0] not in UID_List:
					UID_List.append(row[0])
		
		ea_DictList = []
		
		for d in UID_List:
			
			ea_Dict = {"ObjectID":d,}
			
			with da.SearchCursor(joinFeature, ["OBJECTID", joinField]) as cursor:
				for row in cursor:
					if row[0] == d:
						ea_Dict['Attribute'] = row[1]
			
			ea_DictList.append(ea_Dict)
		
		with da.UpdateCursor(self.feature, ["NEAR_FID", updateField]) as cursor:
			for row in cursor:
				for dictionary in ea_DictList:
					
					if row[0] == dictionary["ObjectID"]:
						row[1] = dictionary['Attribute']
						
						cursor.updateRow(row)
		
		management.DeleteField(self.feature, ['NEAR_FID', 'NEAR_DIST'])
		
		return

################################################################################################################################################

	def extractHydroAttributes(self, joinFeature):
		
		# Perform Near Analysis
		analysis.Near(self.feature, joinFeature, '', 'NO_LOCATION', '', 'GEODESIC')
		
		# Add Hydrology Fields to self
		[management.AddField(self.feature, i, "TEXT") for i in ['Hydro_Name', 'Hydro_Type']]
		management.AddField(self.feature, "Hydro_Dist", "DOUBLE")
		management.AddField(self.feature, "FCode", "LONG")

		Near_FC = []

		# Identify Unique Feature Classes from the NEAR_FC Field and add it to the Near_FC List
		with da.SearchCursor(self.feature, "NEAR_FC") as cursor:
			for row in cursor:
				if row[0] not in Near_FC:
					Near_FC.append(row[0])
		
		# Loop through indices in the Near_FC list
		for fc in Near_FC:
			
			# Create a new dictionary with the Near_FC index as a key/value
			ea_Dict = {'NEAR_FC': fc,}
			
			# Use a Search Cursor to identify each feature that's associated with Nearest Featureclass
			with da.SearchCursor(self.feature, ["NEAR_FC", "NEAR_FID"]) as cursor:
				NEAR_FID = []
				for row in cursor:
					if row[0] == fc:
						NEAR_FID.append(row[1])
						
				ea_Dict['NEAR_FID'] = NEAR_FID
			
			fc_DictList = []
			
			with da.SearchCursor(ea_Dict['NEAR_FC'], ['OBJECTID', 'GNIS_Name', 'FCode']) as cursor:
				for row in cursor:
					if row[0] in ea_Dict['NEAR_FID']:
						fc_DictList.append( {'NEAR_FID':row[0], 'GNIS_Name':row[1], 'FCode':row[2]} )
			
			for dictionary in fc_DictList:
				with da.UpdateCursor(self.feature, ["NEAR_FC", "NEAR_FID", "Hydro_Name", "Hydro_Dist", "NEAR_DIST", "FCode"]) as cursor:
					for row in cursor:
						if row[0] == fc and row[1] == dictionary["NEAR_FID"]:
							row[2] = dictionary['GNIS_Name']
							row[3] = row[4]
							row[5] = dictionary['FCode']
							
							cursor.updateRow(row)
		
		# Create Pandas DataFrame from FCode.CSV
		FCodeDF = pd.DataFrame(pd.read_csv(r'\\tts153fs1.TT.LOCAL\GROUPS\Cultural Resources\GIS_Library\Tools\Tables\NHD_FCode.csv'))
		
		with da.UpdateCursor(self.feature, ["FCode", "Hydro_Type", "Hydro_Name"]) as cursor:
			for row in cursor:
				
				for i in range(len(FCodeDF)):
					
					if row[0] == FCodeDF['FCode'].loc[i]:
						row[1] = FCodeDF['Feature Type'].iloc[i] + ':  ' + FCodeDF['Description'].loc[i]
						
						cursor.updateRow(row)
				
				if row[2] == None:
					row[2] = 'Unnamed Hydrologic Feature'
					
					cursor.updateRow(row)
		
		management.DeleteField(self.feature, ['FCode', 'NEAR_FC', 'NEAR_FID', 'NEAR_DIST'])
		
		return

################################################################################################################################################

	def extractElevationSlopeAttributes_poly(self, UID_List, raster, *args):
		
		# Create Zonal Statistics Table
		zTable = sa.ZonalStatisticsAsTable(self.feature, "SITE_ID", raster, "in_memory/temp", '', "MIN_MAX_MEAN")
		
		ea_DictList = []
		
		for d in UID_List:
			
			ea_Dict = {"SITE_ID":d,}
			
			# Use Search Cursor to Identify Attribute values assigned to Unique IDs and add them to Dictionary
			with da.SearchCursor(zTable, ["SITE_ID", "MEAN", "MIN", "MAX"]) as cursor:
				for row in cursor:
					if row[0] == d:
						ea_Dict['MEAN'] = row[1]
						ea_Dict['MIN'] = row[2]
						ea_Dict['MAX'] = row[3]
			
			ea_DictList.append(ea_Dict)
		
		with da.UpdateCursor(self.feature, ['SITE_ID', args[0], args[1], args[2]]) as cursor:
			for row in cursor:
				for dictionary in ea_DictList:
					
					if row[0] == dictionary['SITE_ID']:
						row[1] = dictionary['MEAN']
						row[2] = dictionary['MIN']
						row[3] = dictionary['MAX']
						
						cursor.updateRow(row)
		
		management.Delete(zTable)
		
		return

################################################################################################################################################

	def extractElevationSlopeAttributes_point(self, UID_List, *args):
		
		# Create Zonal Statistics Table
		zTable = sa.ZonalStatisticsAsTable(self.feature, "SITE_ID", args[0], "in_memory/temp", '', "MEAN")
		
		ea_DictList = []
		
		for d in UID_List:
			
			ea_Dict = {"SITE_ID":d,}
			
			# Use Search Cursor to Identify Attribute values assigned to Unique IDs and add them to Dictionary
			with da.SearchCursor(zTable, ["SITE_ID", "MEAN"]) as cursor:
				for row in cursor:
					if row[0] == d:
						ea_Dict['MEAN'] = row[1]
			
			ea_DictList.append(ea_Dict)
		
		with da.UpdateCursor(self.feature, ['SITE_ID', args[1]]) as cursor:
			for row in cursor:
				for dictionary in ea_DictList:
					
					if row[0] == dictionary['SITE_ID']:
						row[1] = dictionary['MEAN']
						
						cursor.updateRow(row)
		
		management.Delete(zTable)
		
		return

################################################################################################################################################

	def extractAspectAttributes(self, UID_List, *args):
		
		# Create Zonal Statistics Table
		zTable = sa.ZonalStatisticsAsTable(self.feature, "SITE_ID", args[0], "in_memory/temp", '', "MEAN")
		
		ea_DictList = []
		
		for d in UID_List:
			
			ea_Dict = {"SITE_ID":d,}
			
			# Use Search Cursor to Identify Attribute values assigned to Unique IDs and add them to Dictionary
			with da.SearchCursor(zTable, ["SITE_ID", "MEAN"]) as cursor:
				for row in cursor:
					if row[0] == d:
						
						# Reclassify Aspect Raster
						if row[1] > 0 and row[1] <= 22.5:
							ea_Dict['Aspect'] = 'North'
						elif row[1] > 22.5 and row[1] <= 67.5:
							ea_Dict['Aspect'] = 'Northeast'
						elif row[1] > 67.5 and row[1] <= 112.5:
							ea_Dict['Aspect'] = 'East'
						elif row[1] > 112.5 and row[1] <= 157.5:
							ea_Dict['Aspect'] = 'Southeast'
						elif row[1] > 157.5 and row[1] <= 202.5:
							ea_Dict['Aspect'] = 'South'
						elif row[1] > 202.5 and row[1] <= 247.5:
							ea_Dict['Aspect'] = 'Southwest'
						elif row[1] > 247.5 and row[1] <= 292.5:
							ea_Dict['Aspect'] = 'West'
						elif row[1] > 247.5 and row[1] <= 292.5:
							ea_Dict['Aspect'] = 'Northwest'
						elif row[1] > 292.5 and row[1] <= 337.5:
							ea_Dict['Aspect'] = 'Northwest'
						elif row[1] > 337.5 and row[1] <= 360:
							ea_Dict['Aspect'] = 'North'
						else:
							ea_Dict['Aspect'] = 'Flat'
			
			ea_DictList.append(ea_Dict)

		with da.UpdateCursor(self.feature, ['SITE_ID', args[1]]) as cursor:
			for row in cursor:
				for dictionary in ea_DictList:
					
					if row[0] == dictionary['SITE_ID']:
						row[1] = dictionary['Aspect']
						
						cursor.updateRow(row)
		
		management.Delete(zTable)
		
		return
	
"""
========================================================================
Site_Attribute_Extraction.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
12/14/2017		MF			Created new version of tool
12/20/2017		MF			Added Hydrology function
========================================================================
This script is designed to drastically reduce the amount of working hours
required to gather basic spatial attributes related to the location of
cultural sites.  A single Point feature class, as is an ID field
for the feature class, and an output feature class are the only required
inputs.  All other input datasets are not required for the script to run.
"""

if __name__ == '__main__':
	
	''' Collect Required Parameters and Initialize Script Output '''

	# Collect Required Datasets
	arg1 = GetParameterAsText(0) # Input Featureclass
	arg2 = GetParameterAsText(1) # Input Featureclass Field
	arg3 = GetParameterAsText(2) # Output Featureclass
	
	# Write to Log
	writeLog(arg1, arg2, arg3)
	
	# Create New Feature
	mainFeature = outputDataset(inputDataset(arg1).createNewFeatureClass(arg3))

	if mainFeature.desc.shapeType == 'Polygon':
		textFields = ["SITE_ID"]
		numFields = ["NORTHING_m", "EASTING_m", "ACRES"]

	elif mainFeature.desc.shapeType == 'Point':
		textFields = ["SITE_ID"]
		numFields = ["NORTHING_m", "EASTING_m"]

	else:
		AddError("Input Feature geometry type must be 'Point' or 'Polygon'")
		sys.exit()
	
	# Add Fields
	mainFeature.addFields(textFields=textFields, numFields=numFields)
	
	# Extract Primary Feature Attributes
	mainFeature.addPrimaryAttributes(arg1, arg2)
	
	# Collect Unique IDs
	UIDs = mainFeature.collectUIDs()
	
	''' Collect and Process Optional Spatial Join Datasets  '''
	
	processJoinAttributes = []

	# Create New Fields List
	textFields = []

	# Collect Optional Datasets
	arg4 = GetParameterAsText(3) # State Featureclass
	arg5 = GetParameterAsText(4) # State ID Field
	if arg4 != '' and arg5 != '':
		textFields.append('State')
		processJoinAttributes.append(['State', arg4, arg5])
		
	arg6 = GetParameterAsText(5) # County Featureclass
	arg7 = GetParameterAsText(6) # County ID Field
	if arg6 != '' and arg7 != '':
		textFields.append('County')
		processJoinAttributes.append(['County', arg6, arg7])

	arg8 = GetParameterAsText(7) # Quadrangle Featureclass
	arg9 = GetParameterAsText(8) # Quadrangle ID Field
	arg10 = GetParameterAsText(9) # Quadrangle Date Field
	if arg8 != '' and arg9 != '':
		textFields.append('Quad')
	
	arg11 = GetParameterAsText(10) # USGS Basin Featureclass
	arg12 = GetParameterAsText(11) # USGS Basin ID Field
	if arg11 != '' and arg12 != '':
		textFields.append('Basin')
		processJoinAttributes.append(['Basin', arg11, arg12])
	
	arg13 = GetParameterAsText(12) # USGS SubBasin Featureclass
	arg14 = GetParameterAsText(13) # USGS SubBasin ID Field
	if arg13 != '' and arg14 != '':
		textFields.append('SubBasin')
		processJoinAttributes.append(['SubBasin', arg13, arg14])
	
	# Add Optional Join Fields
	mainFeature.addFields(textFields=textFields)
	
	# Extract Optional Dataset Attributes
	for item in processJoinAttributes:
		mainFeature.extractJoinAttributes(UIDs, item[0], item[1], item[2])
	
	# Extract Quadrangle Attributes
	if arg9 != '' and arg10 != '':
		mainFeature.extractQuadAttributes(UIDs, arg8, arg9, arg10)
	elif arg9 != '' and arg10 == '':
		mainFeature.extractQuadAttributes(UIDs, arg8, arg9)
	
	''' Collect and Process Optional Near Datasets '''
	
	processNearAttributes = []
	
	textFields = []
	
	arg15 = GetParameterAsText(14) # Populated Place Featureclass
	arg16 = GetParameterAsText(15) # Populated Place ID Field
	if arg15 != '' and arg16 != '':
		textFields.append('Populated_Place')
		processNearAttributes.append(['Populated_Place', arg15, arg16])

	arg17 = GetParameterAsText(16) # Major Road Featureclass
	arg18 = GetParameterAsText(17) # Major Road ID Field
	if arg17 != '' and arg18 != '':
		textFields.append('Major_Road')
		processNearAttributes.append(['Major_Road', arg17, arg18])
		
	arg19 = GetParameterAsText(18) # Local Road Featureclass
	arg20 = GetParameterAsText(19) # Local Road ID Field
	if arg19 != '' and arg20 != '':
		textFields.append('Local_Road')
		processNearAttributes.append(['Local_Road', arg19, arg20])
	
	# Add Optional Near Fields
	mainFeature.addFields(textFields=textFields)
	
	for item in processNearAttributes:
		mainFeature.extractNearAttributes(item[0], item[1], item[2])
		
	''' Collect and Process Hydro Datasets '''

	arg21 = GetParameterAsText(20)

	if arg21 != '':
		mainFeature.extractHydroAttributes(arg21.split(';'))
	
	''' Collect and Process Optional Spatial Datasets '''
	
	processSpatialAttributes = []
	
	# Create New Fields List for Spatial Data
	numFields = []
	textFields = []
	
	arg22 = GetParameterAsText(21) # Elevation Raster Dataset
	arg23 = GetParameterAsText(22) # Slope Raster Dataset
	arg24 = GetParameterAsText(23) # Aspect Raster Dataset
	
	if mainFeature.desc.shapeType == 'Polygon':
		if arg22 != '':
			numFields.append('Elevation_Avg')
			numFields.append('Elevation_Min')
			numFields.append('Elevation_Max')
			
			processSpatialAttributes.append([arg22, 'Elevation_Avg', 'Elevation_Min', 'Elevation_Max'])
			
		if arg23 != '':
			numFields.append('Slope_Avg')
			numFields.append('Slope_Min')
			numFields.append('Slope_Max')
			
			processSpatialAttributes.append([arg23, 'Slope_Avg', 'Slope_Min', 'Slope_Max'])
			
		if arg24 != '':
			textFields.append('Aspect')
			
	elif mainFeature.desc.shapeType == 'Point':
		if arg22 != '':
			numFields.append('Elevation')
			processSpatialAttributes.append([arg22, 'Elevation'])
			
		if arg23 != '':
			numFields.append('Slope')
			processSpatialAttributes.append([arg23, 'Slope'])
			
		if arg24 != '':
			textFields.append('Aspect')
	
	# Add Spatial Dataset Fields
	mainFeature.addFields(numFields=numFields, textFields=textFields)
	
	# Extract Spatial Dataset Attributes
	if mainFeature.desc.shapeType == 'Polygon':
		for item in processSpatialAttributes:
			mainFeature.extractElevationSlopeAttributes_poly(UIDs, item[0], item[1], item[2], item[3])
	
	elif mainFeature.desc.shapeType == 'Point':
		for item in processSpatialAttributes:
			mainFeature.extractElevationSlopeAttributes_point(UIDs, item[0], item[1])
	
	# Extract Aspect Attributes
	if arg24 != '':
		mainFeature.extractAspectAttributes(UIDs, arg23, 'Aspect')
