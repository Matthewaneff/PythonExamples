from arcpy import *
import os, sys, datetime
import pandas as pd
from pandas import DataFrame

if GetParameter(0) == False:
	sys.exit()

def getSiteList(resourceLyr, selectionLyr_1, selectionLyr_2):
	
	management.SelectLayerByLocation(resourceLyr, "INTERSECT", selectionLyr_1, '', 'NEW_SELECTION')
	
	selectionList_1 = []
	with da.SearchCursor(resourceLyr, "OBJECTID") as cursor:
		for row in cursor:
			selectionList_1.append(row[0])
	
	management.SelectLayerByLocation(resourceLyr, "INTERSECT", selectionLyr_2, '', 'NEW_SELECTION')
	
	selectionList_2 = []
	with da.SearchCursor(resourceLyr, "OBJECTID") as cursor:
		for row in cursor:
			if row[0] not in selectionList_1:
				selectionList_2.append(row[0])
	
	return selectionList_1, selectionList_2

def getAecomSiteList(resourceLyr, selectionLyr_1, selectionLyr_2, selectionLyr_3):
	
	management.SelectLayerByLocation(resourceLyr, "INTERSECT", selectionLyr_1, '', 'NEW_SELECTION')
	
	selectionList_1 = []
	with da.SearchCursor(resourceLyr, "OBJECTID") as cursor:
		for row in cursor:
			selectionList_1.append(row[0])	

	management.SelectLayerByLocation(resourceLyr, "INTERSECT", selectionLyr_2, '', 'NEW_SELECTION')
	
	selectionList_2 = []
	with da.SearchCursor(resourceLyr, "OBJECTID") as cursor:
		for row in cursor:
			if row[0] not in selectionList_1:
				selectionList_2.append(row[0])

	management.SelectLayerByLocation(resourceLyr, "INTERSECT", selectionLyr_3, '', 'NEW_SELECTION')
	
	selectionList_3 = []
	with da.SearchCursor(resourceLyr, "OBJECTID") as cursor:
		for row in cursor:
			if row[0] not in selectionList_1 and row[0] not in selectionList_2:
				selectionList_3.append(row[0])
	
	return selectionList_1, selectionList_2, selectionList_3


def BatchSelectByLocation(resource, layers):
	
	for lyr in layers:
		management.SelectLayerByLocation(lyr, "INTERSECT", resource)
	
	return

#######################################################################

# Collect Resources
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

# Convert Resources to Layers
for item in [siteLine, sitePoint, sitePoly, iso]:
	management.MakeFeatureLayer(item[0], item[1], "NOT DataSource = 'GLO'")
	
for item in [monPoint, monPoly, monLine, aecomPoint, aecomPoly, aecomLine]:
	management.MakeFeatureLayer(item[0], item[1])

# Specify Fields
lineFields = ['OBJECTID', 'SiteNumber', 'TempNumber', 'SiteType', 'Primary_site_type','NR_Status', 'Describe_', "Page_No", "ResourceType", "Exhibit", "County"]
polyFields = ['OBJECTID', 'SiteNumber', 'TempNumber', 'SiteType', 'Primary_site_type','NR_Status', 'Describe_', "Page_No", "ResourceType", "Exhibit", "County"]
pointFields = ['OBJECTID', 'SiteNumber', 'TempNumber', 'SiteType', 'Primary_site_type','NR_Status', 'Describe_', "Page_No", "ResourceType", "Exhibit", "County"]
isoFields = ['OBJECTID', 'IsolateNumber', 'TempNumber', 'SiteType', 'FeatArtType', 'Describe_', "Page_No", "ResourceType", "Exhibit", "County"]
monPointFields = ['OBJECTID', 'SiteNumber', 'TempNumber', 'Component', 'Describe_', 'NR_Status', "Page_No", "ResourceType", "Exhibit", "County"]
monPolyFields = ['OBJECTID', 'SiteNumber', 'TempNumber', 'Component', 'Describe_', 'NR_Status', "Page_No", "ResourceType", "Exhibit", "County"]
monLineFields = ['OBJECTID', 'SiteNumber', 'TempNumber', 'Component', 'Describe_', 'NR_Status', "Page_No", "ResourceType", "Exhibit", "County"]

# Collect Project Features
constructionFP = [r'\\tts153fs1.TT.LOCAL\PROJECTS\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\12_December_2017\B2H_Project Features_FASC_20160902.gdb\Disturbance\Construction', "Construction"]
projectBoundary = [r'\\tts153fs1.TT.LOCAL\PROJECTS\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\12_December_2017\B2H_Project Features_FASC_20160902.gdb\Site_Boundary\Site_Boundary', "Boundary"]
landOwnership = [r'\\tts153fs1.TT.LOCAL\PROJECTS\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\LandStatus\20161108_B2HLandStatus\land_lines.gdb\ownership_poly_dissolve', "Ownership"]
viewshed = [r'\\tts153fs1.TT.LOCAL\PROJECTS\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\12_December_2017\AECOM\B2H_10202017\Viewshed_100416.gdb\dem_visible', "Viewshed"]

# Convert Project Features to Layers
for item in [constructionFP, projectBoundary, landOwnership, viewshed]:
	management.MakeFeatureLayer(item[0], item[1])

# Get Site Lists
sPointList_c, sPointList_b = getSiteList("Site_Point", "Construction", "Boundary")
sPolyList_c, sPolyList_b = getSiteList("Site_Poly", "Construction", "Boundary")
sLineList_c, sLineList_b = getSiteList("Site_Line", "Construction", "Boundary")
mPointList_c, mPointList_b = getSiteList("Monitoring_Point", "Construction", "Boundary")
mLineList_c, mLineList_b = getSiteList("Monitoring_Line", "Construction", "Boundary")
mPolyList_c, mPolyList_b = getSiteList("Monitoring_Poly", "Construction", "Boundary")
isoList_c, isoList_b = getSiteList("Isolate", "Construction", "Boundary")
aecomPointList_c, aecomPointList_b, aecomPointList_v = getAecomSiteList("AECOM_Point", "Construction", "Boundary", "Viewshed")
aecomPolyList_c, aecomPolyList_b, aecomPolyList_v = getAecomSiteList("AECOM_Polygon", "Construction", "Boundary", "Viewshed")
aecomLineList_c, aecomLineList_b, aecomLineList_v = getAecomSiteList("AECOM_Polyline", "Construction", "Boundary", "Viewshed")

# Create CSV Writer
writer = pd.ExcelWriter(r'\\tts153fs1.TT.LOCAL\PROJECTS\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\12_December_2017\Exhibit_S_Resource_Table.xls')

#########################################################################################################################################################

# Loop through datasets
siteDictList = []

for fc in [
			[sPointList_c, pointFields, "Site_Point"],
			[sPolyList_c, polyFields, "Site_Poly"],
			[sLineList_c, lineFields, "Site_Line"],
		]:
				
	for i in fc[0]:
		
		management.SelectLayerByAttribute(fc[2], "NEW_SELECTION", "OBJECTID = {}".format(i))
		
		BatchSelectByLocation(fc[2], ["Construction", "Ownership"])
		
		dictionary = {}
		
		with da.SearchCursor(fc[2], fc[1]) as cursor:
			for row in cursor:
				dictionary['ObjectID'] = row[0]
				dictionary['Smithsonian #'] = row[1]
				dictionary['Temporary ID'] = row[2]
				dictionary['Time Period'] = row[3]
				dictionary['Site Type'] = row[4]
				dictionary['Resource Type'] = row[8]
				dictionary['Exhibit S Attachment'] = row[9]
				dictionary['County'] = row[10]
				dictionary['NRHP Eligibility Recommendation'] = row[5]
				
				if dictionary['Site Type'] == 'see Describe_ field':
					dictionary['Site Type'] = row[6]
					
				dictionary['Page Number'] = row[7]
		
		with da.SearchCursor("Construction", ["ROUTE", "FEATURE"]) as cursor:
			routes = []
			components = []
			for row in cursor:
				routes.append(row[0])
				components.append('{} - {}'.format(row[0], row[1]))
			dictionary['Project Route(s)'] = ', '.join(routes)
			dictionary['Project Component'] = '; '.join(components)
		
		with da.SearchCursor("Ownership", "PROPERTY_STATUS") as cursor:
			propStatus = []
			for row in cursor:
				propStatus.append(row[0])
			dictionary['Property Status'] = ', '.join(propStatus)
		
		dictionary['Source'] = fc[2]
				
		siteDictList.append(dictionary)
	
for fc in [
			[sPointList_b, pointFields, "Site_Point"],
			[sPolyList_b, polyFields, "Site_Poly"],
			[sLineList_b, lineFields, "Site_Line"],
		]:
			
	for i in fc[0]:
		
		management.SelectLayerByAttribute(fc[2], "NEW_SELECTION", "OBJECTID = {}".format(i))
		
		BatchSelectByLocation(fc[2], ["Boundary", "Ownership"])
		
		dictionary = {}
		
		with da.SearchCursor(fc[2], fc[1]) as cursor:
			for row in cursor:
				dictionary['ObjectID'] = row[0]
				dictionary['Smithsonian #'] = row[1]
				dictionary['Temporary ID'] = row[2]
				dictionary['Time Period'] = row[3]
				dictionary['Site Type'] = row[4]
				dictionary['Resource Type'] = row[8]
				dictionary['Exhibit S Attachment'] = row[9]
				dictionary['County'] = row[10]
				dictionary['NRHP Eligibility Recommendation'] = row[5]

				if dictionary['Site Type'] == 'see Describe_ field':
					dictionary['Site Type'] = row[6]
				
				dictionary['Page Number'] = row[7]
		
		with da.SearchCursor("Boundary", ["ROUTE", "FEATURE"]) as cursor:
			routes = []
			components = []
			for row in cursor:
				routes.append(row[0])
				components.append('{} - {}'.format(row[0], row[1]))
			dictionary['Project Route(s)'] = ', '.join(routes)
			dictionary['Project Component'] = '; '.join(components)
		
		with da.SearchCursor("Ownership", "PROPERTY_STATUS") as cursor:
			propStatus = []
			for row in cursor:
				propStatus.append(row[0])
			dictionary['Property Status'] = ', '.join(propStatus)
		
		dictionary['Source'] = fc[2]
		
		siteDictList.append(dictionary)			
			
SiteDF = DataFrame(siteDictList)

SiteDF.to_excel(writer, sheet_name='Sites', columns=['ObjectID', 'Smithsonian #', 'Temporary ID', 'Time Period', 'Site Type',
																				'Resource Type', 'NRHP Eligibility Recommendation',
																				'Project Route(s)', 'Project Component', 'County', 'Property Status',
																				'Resource Type', 'Exhibit S Attachment', 'Source', 'Page Number'], index=False)
																				
#########################################################################################################################################################

monitoringDictList = []

for fc in [
			[mPointList_c, monPointFields, "Monitoring_Point"],
			[mLineList_c, monLineFields, "Monitoring_Line"],
			[mPolyList_c, monPolyFields, "Monitoring_Poly"],
		]:
				
	for i in fc[0]:
		
		management.SelectLayerByAttribute(fc[2], "NEW_SELECTION", "OBJECTID = {}".format(i))
		
		BatchSelectByLocation(fc[2], ["Construction", "Ownership"])
		
		dictionary = {}
		
		with da.SearchCursor(fc[2], fc[1]) as cursor:
			for row in cursor:
				dictionary['ObjectID'] = row[0]
				dictionary['Smithsonian #'] = row[1]
				dictionary['Temporary ID'] = row[2]
				dictionary['Time Period'] = row[3]
				dictionary['Site Type'] = row[4]
				dictionary['Resource Type'] = row[7]
				dictionary['Exhibit S Attachment'] = row[8]
				dictionary['County'] = row[9]
				dictionary['NRHP Eligibility Recommendation'] = row[5]
				dictionary['Page Number'] = row[6]
		
		with da.SearchCursor("Construction", ["ROUTE", "FEATURE"]) as cursor:
			routes = []
			components = []
			for row in cursor:
				routes.append(row[0])
				components.append('{} - {}'.format(row[0], row[1]))
			dictionary['Project Route(s)'] = ', '.join(routes)
			dictionary['Project Component'] = '; '.join(components)
		
		with da.SearchCursor("Ownership", "PROPERTY_STATUS") as cursor:
			propStatus = []
			for row in cursor:
				propStatus.append(row[0])
			dictionary['Property Status'] = ', '.join(propStatus)
		
		dictionary['Source'] = fc[2]
		
		monitoringDictList.append(dictionary)

for fc in [
			[mPointList_b, monPointFields, "Monitoring_Point"],
			[mLineList_b, monLineFields, "Monitoring_Line"],
			[mPolyList_b, monPolyFields, "Monitoring_Poly"],
		]:
				
	for i in fc[0]:
		
		management.SelectLayerByAttribute(fc[2], "NEW_SELECTION", "OBJECTID = {}".format(i))
		
		BatchSelectByLocation(fc[2], ["Boundary", "Ownership"])
		
		dictionary = {}
		
		with da.SearchCursor(fc[2], fc[1]) as cursor:
			for row in cursor:
				dictionary['ObjectID'] = row[0]
				dictionary['Smithsonian #'] = row[1]
				dictionary['Temporary ID'] = row[2]
				dictionary['Time Period'] = row[3]
				dictionary['Site Type'] = row[4]
				dictionary['Resource Type'] = row[7]
				dictionary['Exhibit S Attachment'] = row[8]
				dictionary['County'] = row[9]
				dictionary['NRHP Eligibility Recommendation'] = row[5]
				dictionary['Page Number'] = row[6]
		
		with da.SearchCursor("Boundary", ["ROUTE", "FEATURE"]) as cursor:
			routes = []
			components = []
			for row in cursor:
				routes.append(row[0])
				components.append('{} - {}'.format(row[0], row[1]))
			dictionary['Project Route(s)'] = ', '.join(routes)
			dictionary['Project Component'] = '; '.join(components)
		
		with da.SearchCursor("Ownership", "PROPERTY_STATUS") as cursor:
			propStatus = []
			for row in cursor:
				propStatus.append(row[0])
			dictionary['Property Status'] = ', '.join(propStatus)
		
		dictionary['Source'] = fc[2]
				
		monitoringDictList.append(dictionary)

MonitoringDF = DataFrame(monitoringDictList)

MonitoringDF.to_excel(writer, sheet_name='Class I Updates', columns=['ObjectID', 'Smithsonian #', 'Temporary ID', 'Time Period', 'Site Type',
																				'Resource Type', 'NRHP Eligibility Recommendation',
																				'Project Route(s)', 'Project Component', 'County', 'Property Status',
																				'Resource Type', 'Exhibit S Attachment', 'Source', 'Page Number'], index=False)

#########################################################################################################################################################

isoDictList = []

for fc in [
			[isoList_c, isoFields, "Isolate"]
		]:
				
	for i in fc[0]:
		
		management.SelectLayerByAttribute(fc[2], "NEW_SELECTION", "OBJECTID = {}".format(i))
		
		BatchSelectByLocation(fc[2], ["Construction", "Ownership"])
		
		dictionary = {}
		
		with da.SearchCursor(fc[2], fc[1]) as cursor:
			for row in cursor:
				dictionary['ObjectID'] = row[0]
				dictionary['Isolate #'] = row[1]
				dictionary['Temporary ID'] = row[2]
				dictionary['Time Period'] = row[3]
				dictionary['Site Type'] = row[4]
				dictionary['Resource Type'] = row[7]
				dictionary['County'] = row[9]
				dictionary['Exhibit S Attachment'] = row[8]

				if dictionary['Site Type'] == 'see Describe_ field':
					dictionary['Site Type'] = row[5]
				
				dictionary['Page Number'] = row[6]
		
		with da.SearchCursor("Construction", ["ROUTE", "FEATURE"]) as cursor:
			routes = []
			components = []
			for row in cursor:
				routes.append(row[0])
				components.append('{} - {}'.format(row[0], row[1]))
			dictionary['Project Route(s)'] = ', '.join(routes)
			dictionary['Project Component'] = '; '.join(components)
		
		with da.SearchCursor("Ownership", "PROPERTY_STATUS") as cursor:
			propStatus = []
			for row in cursor:
				propStatus.append(row[0])
			dictionary['Property Status'] = ', '.join(propStatus)
		
		dictionary['Source'] = fc[2]
		
		isoDictList.append(dictionary)

for fc in [
			[isoList_b, isoFields, "Isolate"]
		]:
				
	for i in fc[0]:
		
		management.SelectLayerByAttribute(fc[2], "NEW_SELECTION", "OBJECTID = {}".format(i))
		
		BatchSelectByLocation(fc[2], ["Boundary", "Ownership"])
		
		dictionary = {}
		
		with da.SearchCursor(fc[2], fc[1]) as cursor:
			for row in cursor:
				dictionary['ObjectID'] = row[0]
				dictionary['Isolate #'] = row[1]
				dictionary['Temporary ID'] = row[2]
				dictionary['Time Period'] = row[3]
				dictionary['Site Type'] = row[4]
				dictionary['Resource Type'] = row[7]
				dictionary['County'] = row[9]
				dictionary['Exhibit S Attachment'] = row[8]

				if dictionary['Site Type'] == 'see Describe_ field':
					dictionary['Site Type'] = row[5]
				
				dictionary['Page Number'] = row[6]
		
		with da.SearchCursor("Boundary", ["ROUTE", "FEATURE"]) as cursor:
			routes = []
			components = []
			for row in cursor:
				routes.append(row[0])
				components.append('{} - {}'.format(row[0], row[1]))
			dictionary['Project Route(s)'] = ', '.join(routes)
			dictionary['Project Component'] = '; '.join(components)
		
		with da.SearchCursor("Ownership", "PROPERTY_STATUS") as cursor:
			propStatus = []
			for row in cursor:
				propStatus.append(row[0])
			dictionary['Property Status'] = ', '.join(propStatus)
		
		dictionary['Source'] = fc[2]
		
		isoDictList.append(dictionary)

IsolateDF = DataFrame(isoDictList)

IsolateDF.to_excel(writer, sheet_name='Isolates', columns=['ObjectID', 'Isolate #', 'Temporary ID', 'Time Period',
															'Site Type', 'Resource Type', 'Project Route(s)', 
															'Project Component', 'County', 'Property Status',
															'Resource Type', 'Exhibit S Attachment', 'Source', 'Page Number'], index=False)

#########################################################################################################################################################

aecomDictList = []

for fc in [
			[aecomPointList_c, pointFields, "AECOM_Point"],
			[aecomPolyList_c, polyFields, "AECOM_Polygon"],
			[aecomLineList_c, lineFields, "AECOM_Polyline"],
		]:
				
	for i in fc[0]:
		
		management.SelectLayerByAttribute(fc[2], "NEW_SELECTION", "OBJECTID = {}".format(i))
		
		BatchSelectByLocation(fc[2], ["Construction", "Ownership", "Viewshed"])
		
		dictionary = {}
		
		with da.SearchCursor(fc[2], fc[1]) as cursor:
			for row in cursor:
				dictionary['ObjectID'] = row[0]
				dictionary['Smithsonian #'] = row[1]
				dictionary['Temporary ID'] = row[2]
				dictionary['Time Period'] = row[3]
				dictionary['Site Type'] = row[4]
				dictionary['Resource Type'] = row[8]
				dictionary['County'] = row[10]
				dictionary['Exhibit S Attachment'] = row[9]
				dictionary['NRHP Eligibility Recommendation'] = row[5]
				
				if dictionary['Site Type'] == 'see Describe_ field':
					dictionary['Site Type'] = row[6]
					
				dictionary['Page Number'] = row[7]
		
		with da.SearchCursor("Construction", ["ROUTE", "FEATURE"]) as cursor:
			routes = []
			components = []
			for row in cursor:
				routes.append(row[0])
				components.append('{} - {}'.format(row[0], row[1]))
			dictionary['Project Route(s)'] = ', '.join(routes)
			dictionary['Project Component'] = '; '.join(components)
		
		with da.SearchCursor("Ownership", "PROPERTY_STATUS") as cursor:
			propStatus = []
			for row in cursor:
				propStatus.append(row[0])
			dictionary['Property Status'] = ', '.join(propStatus)

		count = int(management.GetCount("Viewshed").getOutput(0))
		
		if count != len(fc[0]):
			dictionary['In Viewshed'] = 'Yes'
		else:
			dictionary['In Viewshed'] = 'No'
		
		dictionary['Source'] = fc[2]
				
		aecomDictList.append(dictionary)
	
for fc in [
			[aecomPointList_b, pointFields, "AECOM_Point"],
			[aecomPolyList_b, polyFields, "AECOM_Polygon"],
			[aecomLineList_b, lineFields, "AECOM_Polyline"],
		]:
			
	for i in fc[0]:
		
		management.SelectLayerByAttribute(fc[2], "NEW_SELECTION", "OBJECTID = {}".format(i))
		
		BatchSelectByLocation(fc[2], ["Boundary", "Ownership", "Viewshed"])
		
		dictionary = {}
		
		with da.SearchCursor(fc[2], fc[1]) as cursor:
			for row in cursor:
				dictionary['ObjectID'] = row[0]
				dictionary['Smithsonian #'] = row[1]
				dictionary['Temporary ID'] = row[2]
				dictionary['Time Period'] = row[3]
				dictionary['Site Type'] = row[4]
				dictionary['Resource Type'] = row[8]
				dictionary['County'] = row[10]
				dictionary['Exhibit S Attachment'] = row[9]
				dictionary['NRHP Eligibility Recommendation'] = row[5]

				if dictionary['Site Type'] == 'see Describe_ field':
					dictionary['Site Type'] = row[6]
				
				dictionary['Page Number'] = row[7]
		
		with da.SearchCursor("Boundary", ["ROUTE", "FEATURE"]) as cursor:
			routes = []
			components = []
			for row in cursor:
				routes.append(row[0])
				components.append('{} - {}'.format(row[0], row[1]))
			dictionary['Project Route(s)'] = ', '.join(routes)
			dictionary['Project Component'] = '; '.join(components)
		
		with da.SearchCursor("Ownership", "PROPERTY_STATUS") as cursor:
			propStatus = []
			for row in cursor:
				propStatus.append(row[0])
			dictionary['Property Status'] = ', '.join(propStatus)

		count = int(management.GetCount("Viewshed").getOutput(0))
		
		if count != len(fc[0]):
			dictionary['In Viewshed'] = 'Yes'
		else:
			dictionary['In Viewshed'] = 'No'
		
		dictionary['Source'] = fc[2]
		
		aecomDictList.append(dictionary)			

for fc in [
			[aecomPointList_v, pointFields, "AECOM_Point"],
			[aecomPolyList_v, polyFields, "AECOM_Polygon"],
			[aecomLineList_v, lineFields, "AECOM_Polyline"],
		]:
			
	for i in fc[0]:
		
		management.SelectLayerByAttribute(fc[2], "NEW_SELECTION", "OBJECTID = {}".format(i))
		
		BatchSelectByLocation(fc[2], ["Boundary", "Ownership", "Viewshed"])
		
		dictionary = {}
		
		with da.SearchCursor(fc[2], fc[1]) as cursor:
			for row in cursor:
				dictionary['ObjectID'] = row[0]
				dictionary['Smithsonian #'] = row[1]
				dictionary['Temporary ID'] = row[2]
				dictionary['Time Period'] = row[3]
				dictionary['Site Type'] = row[4]
				dictionary['Resource Type'] = row[8]
				dictionary['County'] = row[10]
				dictionary['Exhibit S Attachment'] = row[9]
				dictionary['NRHP Eligibility Recommendation'] = row[5]

				if dictionary['Site Type'] == 'see Describe_ field':
					dictionary['Site Type'] = row[6]
				
				dictionary['Page Number'] = row[7]
		
		with da.SearchCursor("Boundary", ["ROUTE", "FEATURE"]) as cursor:
			routes = []
			components = []
			for row in cursor:
				routes.append(row[0])
				components.append('{} - {}'.format(row[0], row[1]))
			dictionary['Project Route(s)'] = ', '.join(routes)
			dictionary['Project Component'] = '; '.join(components)
		
		with da.SearchCursor("Ownership", "PROPERTY_STATUS") as cursor:
			propStatus = []
			for row in cursor:
				propStatus.append(row[0])
			dictionary['Property Status'] = ', '.join(propStatus)
		
		count = int(management.GetCount("Viewshed").getOutput(0))
		
		if count != len(fc[0]):
			dictionary['In Viewshed'] = 'Yes'
		else:
			dictionary['In Viewshed'] = 'No'
		
		dictionary['Source'] = fc[2]
		
		aecomDictList.append(dictionary)	
		
AecomDF = DataFrame(aecomDictList)

AecomDF.to_excel(writer, sheet_name='AECOM Sites', columns=['ObjectID', 'Smithsonian #', 'Temporary ID', 'Time Period', 
													  'Site Type', 'Resource Type', 'NRHP Eligibility Recommendation',
													  'Project Route(s)', 'Project Component', 'County', 
													  'In Viewshed', 'Property Status',
													  'Resource Type', 'Exhibit S Attachment', 'Source', 'Page Number'], index=False)
																				
writer.save()
