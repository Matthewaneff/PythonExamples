import os, sys, datetime
from arcpy import *
import pandas as pd

def main():
	
	# Designate Excel file
	excel = r'\\tts153fs1.TT.LOCAL\PROJECTS\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\12_December_2017\Exhibit_S_Resource_Table.xls'
	
	# Check if Excel file exists
	if not os.path.exists(excel):
		AddError("'Exhibit_S_Resource_Table.xls' does not exist.  Please run 'Run B2H Table' script tool.")
		sys.exit()
	
	# Create layers
	siteLine = [r'\\tts153fs1.TT.LOCAL\PROJECTS\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\12_December_2017\Exhibit_S\Exhibit_S_Database.gdb\Site_line', "Site_Line"]
	sitePoly = [r'\\tts153fs1.TT.LOCAL\PROJECTS\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\12_December_2017\Exhibit_S\Exhibit_S_Database.gdb\Site_polygon', "Site_Poly"]
	sitePoint = [r'\\tts153fs1.TT.LOCAL\PROJECTS\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\12_December_2017\Exhibit_S\Exhibit_S_Database.gdb\Site_point', "Site_Point"]
	iso = [r'\\tts153fs1.TT.LOCAL\PROJECTS\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\12_December_2017\Exhibit_S\Exhibit_S_Database.gdb\Isolate', "Isolate"]
	monPoint = [r'\\tts153fs1.TT.LOCAL\PROJECTS\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\12_December_2017\Exhibit_S\Exhibit_S_Database.gdb\Monitoring_point', "Monitoring_Point"]
	monLine = [r'\\tts153fs1.TT.LOCAL\PROJECTS\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\12_December_2017\Exhibit_S\Exhibit_S_Database.gdb\Monitoring_line', "Monitoring_Line"]
	monPoly = [r'\\tts153fs1.TT.LOCAL\PROJECTS\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\12_December_2017\Exhibit_S\Exhibit_S_Database.gdb\Monitoring_polygon', "Monitoring_Poly"]
	aecomPoint = [r'\\tts153fs1.TT.LOCAL\PROJECTS\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\12_December_2017\Exhibit_S\Exhibit_S_Database.gdb\AECOM_Point', "AECOM_Point"]
	aecomPoly = [r'\\tts153fs1.TT.LOCAL\PROJECTS\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\12_December_2017\Exhibit_S\Exhibit_S_Database.gdb\AECOM_Polyline', "AECOM_Polyline"]
	aecomLine = [r'\\tts153fs1.TT.LOCAL\PROJECTS\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\12_December_2017\Exhibit_S\Exhibit_S_Database.gdb\AECOM_Polygon', "AECOM_Polygon"]

	for item in [siteLine, sitePoint, sitePoly, iso, aecomLine, aecomPoint, aecomPoly, monPoint, monPoly, monLine]:
		management.MakeFeatureLayer(item[0], item[1])

	# Create Geodatabase
	d = datetime.datetime.now()
	sDate = d.strftime("%Y%m%d")
	gdb = management.CreateFileGDB(r'\\tts153fs1.TT.LOCAL\PROJECTS\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\12_December_2017\Exhibit_S', 'Exhibit_S_{}'.format(sDate))

	# Add New FeatureClasses to Geodatabase
	point = management.CreateFeatureclass(gdb, 'Point', "POINT", '', '', '', 26911)
	poly = management.CreateFeatureclass(gdb, 'Polygon', "POLYGON", '', '', '', 26911)
	line = management.CreateFeatureclass(gdb, 'Polyline', "POLYLINE", '', '', '', 26911)

	# Add Fields to FeatureClasses
	for fc in [point, line, poly]:
		
		[management.AddField(fc, i, "TEXT") for i in ["SiteNumber", "TempNumber", "TimePeriod", "SiteType"]]

	'''Begin Analysis'''

	# Convert Excel file to Dataframes for each sheet
	isoDF = pd.DataFrame(pd.read_excel(excel, sheetname='Isolates'), columns=['ObjectID', 'Source'])
	siteDF = pd.DataFrame(pd.read_excel(excel, sheetname='Sites'), columns=['ObjectID', 'Source'])
	monDF = pd.DataFrame(pd.read_excel(excel, sheetname='Class I Updates'), columns=['ObjectID', 'Source'])
	aecDF = pd.DataFrame(pd.read_excel(excel, sheetname='AECOM Sites'), columns=['ObjectID', 'Source'])


	# Perform analysis on Tetra Tech and Aecom Site FeatureClasses
	for df in [siteDF, aecDF]:
		
		# Isolate Unique Source entries in each DataFrame
		lyrs = [str(i) for i in df['Source'].unique()]
		
		for lyr in lyrs:
			
			# Create a temporary DataFrame of only indices that match the source layer
			temp_df = df[df['Source'] == '{}'.format(lyr)]
			
			# Create a tuple from the 'ObjectID' entries
			objectID = tuple([int(i) for i in temp_df['ObjectID']])
			
			# Perform a Select By Attribute analysis, selecting only the ObjectIDs in the ObjectID tuple
			selection = management.SelectLayerByAttribute(lyr, "NEW_SELECTION", "OBJECTID IN {}".format(objectID))
			
			# Identify the shape type, necessary for the following InsertCursor
			shape = Describe(selection).shapeType
			
			# Create InsertCursor based off the shape of the selected layer
			if shape == 'Point':
				inscurs = da.InsertCursor(point, ["SHAPE@", "SiteNumber", "TempNumber", "TimePeriod", "SiteType"])
			elif shape == 'Polyline':
				inscurs = da.InsertCursor(line, ["SHAPE@", "SiteNumber", "TempNumber", "TimePeriod", "SiteType"])
			elif shape == 'Polygon':
				inscurs = da.InsertCursor(poly, ["SHAPE@", "SiteNumber", "TempNumber", "TimePeriod", "SiteType"])
			
			# Create a SearchCursor from the selected layer
			with da.SearchCursor(selection, ["SHAPE@", "SiteNumber", "TempNumber", "SiteType", "Primary_site_type", "Describe_"]) as cursor:
				for row in cursor:
					shape, siteNumber, tempNumber, timePeriod = row[0], row[1], row[2], row[3]
					
					if row[4] != 'see Describe_ field':
						siteType = row[4]
					elif row[4] == 'see Describe_ field':
						siteType = row[5]
					
					inscurs.insertRow([shape, siteNumber, tempNumber, timePeriod, siteType])
			
			del inscurs
	
	# Perform analysis on Isolate FeatureClass
	for df in [isoDF]:
		
		# Create a tuple from the 'ObjectID' entries
		objectID = tuple([int(i) for i in df['ObjectID']])
		
		# Perform a Select By Attribute analysis, selecting only the ObjectIDs in the ObjectID tuple
		selection = management.SelectLayerByAttribute("Isolate", "NEW_SELECTION", "OBJECTID IN {}".format(objectID))
		
		# Create InsertCursor based off the shape of the selected layer
		inscurs = da.InsertCursor(point, ["SHAPE@", "SiteNumber", "TempNumber", "TimePeriod", "SiteType"])

		# Create a SearchCursor from the selected layer
		with da.SearchCursor(selection, ["SHAPE@", "IsolateNumber", "TempNumber", "SiteType", "FeatArtType", "Describe_"]) as cursor:
			for row in cursor:
				shape, siteNumber, tempNumber, timePeriod = row[0], row[1], row[2], row[3]
				
				if row[4] != 'see Description':
					siteType = row[4]
				elif row[4] == 'see Description':
					siteType = row[5]
				
				inscurs.insertRow([shape, siteNumber, tempNumber, timePeriod, siteType])
		
		del inscurs
	
	# Perform analysis on Monitoring FeatureClasses
	for df in [monDF]:
		
		# Isolate Unique Source entries in each DataFrame
		lyrs = [str(i) for i in df['Source'].unique()]
		
		for lyr in lyrs:
			
			# Create a temporary DataFrame of only indices that match the source layer
			temp_df = df[df['Source'] == '{}'.format(lyr)]
			
			# Create a tuple from the 'ObjectID' entries
			objectID = tuple([int(i) for i in temp_df['ObjectID']])
			
			# Perform a Select By Attribute analysis, selecting only the ObjectIDs in the ObjectID tuple
			selection = management.SelectLayerByAttribute(lyr, "NEW_SELECTION", "OBJECTID IN {}".format(objectID))
			
			# Identify the shape type, necessary for the following InsertCursor
			shape = Describe(selection).shapeType
			
			# Create InsertCursor based off the shape of the selected layer
			if shape == 'Point':
				inscurs = da.InsertCursor(point, ["SHAPE@", "SiteNumber", "TempNumber", "TimePeriod", "SiteType"])
			elif shape == 'Polyline':
				inscurs = da.InsertCursor(line, ["SHAPE@", "SiteNumber", "TempNumber", "TimePeriod", "SiteType"])
			elif shape == 'Polygon':
				inscurs = da.InsertCursor(poly, ["SHAPE@", "SiteNumber", "TempNumber", "TimePeriod", "SiteType"])
			
			# Create a SearchCursor from the selected layer
			with da.SearchCursor(selection, ["SHAPE@", "SiteNumber", "TempNumber", "Component", "Describe_"]) as cursor:
				for row in cursor:
					
					inscurs.insertRow([row[0], row[1], row[2], row[3], row[4]])
			
			del inscurs

""" Begin Script Here """

if __name__ == '__main__':
	
	# Collect user entry
	run = GetParameter(0)
	
	# Run Script
	if run == True:
		main()
