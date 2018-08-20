import arcpy, os, csv
from arcpy import *

def write_csv(output_folder, table_name, fields, input_list):
	'''
	This function takes a series of user defined inputs and creates a .CSV file from them
	'output_folder' is the output path where the .CSV will be created
	'table_name' is the title of the .CSV file
	'fields' is a list of strings corresponding to the field names in the dictionary
	'input_list' is a list of dictionaries that will fill the .CSV
	'''
	with open(os.path.join(output_folder, table_name + '.csv'), 'wb') as csvfile:
		fieldnames = fields
		writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
	
		if type(input_list) == list:
			writer.writeheader()
			for row in input_list:
				writer.writerow(row)
		else:
			writer.writeheader()
			writer.writerow(input_list)
	return

"""
========================================================================
Exhibit_S_T3
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
12/19/2016		MF			Created
========================================================================
This script is intended to gather relevant information pertaining to the 
Application for Site Certification for the Boardman to Hemmingway project.
It performs a series of queries to count the number of sites that intersect
the county and route, and then produces two different .CSV files
"""

env.overwriteOutput = "TRUE"

output_folder = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\Application_for_Site_Certification\Exhibit_S_Cultural_Resources\06.ODOE pASC_Jan2017\Table_S_4'
output_folder = str(GetParameter(0))

# Site Points
site_points = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\Survey\2016_BLM_Version.gdb\Site_point'
management.MakeFeatureLayer(site_points, "Sites", "DataSource = 'GPS'")
# Site Polygons
site_polys = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\Survey\2016_BLM_Version.gdb\Site_polygon'
management.MakeFeatureLayer(site_polys, 'Polys', "DataSource = 'GPS'")
# Site Lines
site_lines = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\Survey\2016_BLM_Version.gdb\Site_line'
management.MakeFeatureLayer(site_lines, 'Lines', "DataSource = 'GPS'")
# Route
route = r'C:\Users\Mitchell.Fyock\Desktop\Projects\OR_B2H\GIS\Data\TetraTech\Boardman2Hemmingway_Master.gdb\Project_Infrastructure\Footprint_Merge_Route_Dissolve_OR'
management.MakeFeatureLayer(route, 'Proposed_Route', "FEATURE = 'Proposed Route'")
management.MakeFeatureLayer(route, 'Alternative_Route', "FEATURE = 'Alternative Route'")
# Counties
county = r'G:\Cultural Resources\GIS_Library\UnitedStates\Census_2013\tl_2013_us_county\tl_2013_us_county.shp'
management.MakeFeatureLayer(county, "Counties", "STATEFP = '41' AND NAME IN ('Baker', 'Umatilla', 'Malheur', 'Union', 'Morrow')")

feature_list = ['Sites', 'Polys', 'Lines']

# Create a new feature layer for each county.  Add the county names to a list to be used later for selecting by attributes
counties_list = []
with da.SearchCursor("Counties", "NAME") as cursor:
     for row in cursor:
		 name = row[0]
		 management.MakeFeatureLayer("Counties", name, "NAME = '{}'".format(name))
		 counties_list.append(name)

route_list = []
with da.SearchCursor("Alternative_Route", "ROUTE") as cursor:
     for row in cursor:
		 name = row[0]
		 management.MakeFeatureLayer("Alternative_Route", name, "ROUTE = '{}'".format(name))
		 route_list.append(name)

# Loop through each county, identifying and counting the amount of features that intersect the route within the county boundaries
proposed_route_list = []
for county in counties_list:
	attribute_count = {
	"County": "Proposed Route, " + county + " County",
	"Pre-Contact":0,
	"Historic":0,
	"Multi-Component":0,
	"Unknown":0,
	"Total": 0
	}
	for feature in feature_list:
		management.SelectLayerByLocation(feature, "INTERSECT", county, '', 'NEW_SELECTION')
		management.SelectLayerByLocation(feature, "INTERSECT", 'Proposed_Route', '', 'SUBSET_SELECTION')
		with da.SearchCursor(feature, "SiteType") as cursor:
			for row in cursor:
				entry = row[0].lower()
				attribute_count["Total"] += 1
				if entry == 'pre-contact' or entry == 'prehistoric':
					attribute_count['Pre-Contact'] += 1
				elif entry == 'historic':
					attribute_count['Historic'] += 1
				elif entry == 'multicomponent':
					attribute_count['Multi-Component'] += 1
				elif entry == 'undetermined' or entry == 'unknown':
					attribute_count['Unknown'] += 1
	proposed_route_list.append(attribute_count)

# Write results to a .CSV
fields = ['County', 'Pre-Contact', 'Historic', 'Multi-Component', 'Unknown', 'Total']
write_csv(output_folder, 'S-4_Proposed_Route', fields, proposed_route_list)

# Query and count for alternative route
alternative_route_list = []
for route in route_list:
	attribute_count = {
	"Pre-Contact":0,
	"Historic":0,
	"Multi-Component":0,
	"Unknown":0,
	"Route": route,
	"Total": 0
	}
	for feature in feature_list:
		management.SelectLayerByLocation(feature, "INTERSECT", route, '', 'NEW_SELECTION')
		with da.SearchCursor(feature, "SiteType") as cursor:
			for row in cursor:
				entry = row[0].lower()
				attribute_count["Total"] += 1
				if entry == 'pre-contact' or entry == 'prehistoric':
					attribute_count['Pre-Contact'] += 1
				elif entry == 'historic':
					attribute_count['Historic'] += 1
				elif entry == 'multicomponent':
					attribute_count['Multi-Component'] += 1
				elif entry == 'undetermined' or entry == 'unknown':
					attribute_count['Unknown'] += 1
					
	alternative_route_list.append(attribute_count)

# Write results to a .CSV
fields = ['Route', 'Pre-Contact', 'Historic', 'Multi-Component', 'Unknown', 'Total']
write_csv(output_folder, 'S-4_Alternative_Route', fields, alternative_route_list)

''' Perform Same Query For Monitoring Polygon'''

monitoring_poly = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\Survey\2016_BLM_Version.gdb\Monitoring_polygon'
management.MakeFeatureLayer(monitoring_poly, "MP", "DataSource LIKE 'GPS%'")

proposed_route_list = []

for county in counties_list:
	# Create an empty dictionary	
	attribute_count = {
	"County": "Proposed Route, " + county + " County",
	"Pre-Contact":0,
	"Historic":0,
	"Multi-Component":0,
	"Unknown":0,
	"Total": 0
	}	
	
	management.SelectLayerByLocation("MP", "INTERSECT", county, '', 'NEW_SELECTION')
	management.SelectLayerByLocation("MP", "INTERSECT", 'Proposed_Route', '', 'SUBSET_SELECTION')
	
	with da.SearchCursor("MP", "Component") as cursor:
		for row in cursor:
			entry = row[0].lower()
			attribute_count["Total"] += 1
			if entry == 'pre-contact' or entry == 'prehistoric':
				attribute_count['Pre-Contact'] += 1
			elif entry == 'historic':
				attribute_count['Historic'] += 1
			elif entry == 'multicomponent':
				attribute_count['Multi-Component'] += 1
			elif entry == 'undetermined' or entry == 'unknown':
				attribute_count['Unknown'] += 1
	proposed_route_list.append(attribute_count)

# Write results to a .CSV
fields = ['County', 'Pre-Contact', 'Historic', 'Multi-Component', 'Unknown', 'Total']	
write_csv(output_folder, 'S-4_Proposed_Route_Class_I_Updates', fields, proposed_route_list)

# Query and count for alternative route
alternative_route_list = []
for route in route_list:
	attribute_count = {
	"Pre-Contact":0,
	"Historic":0,
	"Multi-Component":0,
	"Unknown":0,
	"Route": route,
	"Total": 0
	}
		
	management.SelectLayerByLocation(feature, "INTERSECT", route, '', 'NEW_SELECTION')
	
	with da.SearchCursor("MP", "Component") as cursor:
		for row in cursor:
			entry = row[0].lower()
			attribute_count["Total"] += 1
			if entry == 'pre-contact' or entry == 'prehistoric':
				attribute_count['Pre-Contact'] += 1
			elif entry == 'historic':
				attribute_count['Historic'] += 1
			elif entry == 'multicomponent':
				attribute_count['Multi-Component'] += 1
			elif entry == 'undetermined' or entry == 'unknown':
				attribute_count['Unknown'] += 1

	alternative_route_list.append(attribute_count)

fields = ['Route', 'Pre-Contact', 'Historic', 'Multi-Component', 'Unknown', 'Total']
write_csv(output_folder, 'S-4_Alternative_Route_Class_I_Updates', fields, alternative_route_list)
