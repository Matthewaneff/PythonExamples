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
Exhibit_S_T10
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
12/22/2016		MF			Created
========================================================================
Performs a series of queries to gather information pertaining to
Table S-10: NRHP Eligibility Recommendations for Archaeological Sites
within the Analysis Area and creates two .CSV files in a specified folder
"""

env.overwriteOutput = "TRUE"

output_folder = str(GetParameter(0))

# Site Points
site_points = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\Survey\2016_BLM_Version.gdb\Site_point'
management.MakeFeatureLayer(site_points, "Sites", "DataSource = 'GPS' AND NOT NR_Status IS NULL")
# Site Polygons
site_polys = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\Survey\2016_BLM_Version.gdb\Site_polygon'
management.MakeFeatureLayer(site_polys, 'Polys', "DataSource = 'GPS' AND NOT NR_Status IS NULL")
# Site Lines
site_lines = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\Survey\2016_BLM_Version.gdb\Site_line'
management.MakeFeatureLayer(site_lines, 'Lines', "DataSource = 'GPS' AND NOT NR_Status IS NULL")
# Route
route = r'C:\Users\Mitchell.Fyock\Desktop\Projects\OR_B2H\GIS\Data\TetraTech\Boardman2Hemmingway_Master.gdb\Project_Infrastructure\Footprint_Merge_Route_Dissolve_OR'
management.MakeFeatureLayer(route, "Proposed Route", "FEATURE = 'Proposed Route'")
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

routes = []
with da.SearchCursor(route, "ROUTE") as cursor:
     for row in cursor:
		 name = row[0]
		 if name != 'Proposed Route':
			 management.MakeFeatureLayer(route, name, "ROUTE = '{}'".format(name))
			 routes.append(name)

# Loop through each county, identifying and counting the amount of features that intersect the proposed route within the county boundaries
proposed_route_list = []
for county in counties_list:
	proposed_route_count = {
	"County": "Proposed Route, " + county + " County",
	"Eligible":0,
	"Eligible/Not Eligible":0,
	"Eligible/Unevaluated":0,
	"Protected":0,
	"Not Eligible":0,
	"Not Eligible/Non-Contributing":0,
	"Not Eligible/Protected":0,
	"Unevaluated/Protected":0,
	"Unevaluated":0,
	"Unevaluated/Not Eligible":0,
	"Eligible and Part of a District":0,
	}
	for feature in feature_list:
		management.SelectLayerByLocation(feature, "INTERSECT", county, '', 'NEW_SELECTION')
		management.SelectLayerByLocation(feature, "INTERSECT", 'Proposed Route', '', 'SUBSET_SELECTION')
		with da.SearchCursor(feature, "NR_Status") as cursor:
			for row in cursor:
				entry = row[0]
				if entry == 'eligible':
					proposed_route_count['Eligible'] += 1
				elif entry == 'eligible/not eligible':
					proposed_route_count["Eligible/Not Eligible"] += 1
				elif entry == 'eligible/unevaluated':
					proposed_route_count["Eligible/Unevaluated"] += 1
				elif entry == 'protected':
					proposed_route_count['Protected'] += 1
				elif entry == 'not eligible':
					proposed_route_count['Not Eligible'] += 1
				elif entry == 'not eligible/non-contributing':
					proposed_route_count["Not Eligible/Non-Contributing"] += 1
				elif entry == 'not eligible/protected':
					proposed_route_count["Not Eligible/Protected"] += 1
				elif entry == 'unevaluated':
					proposed_route_count['Unevaluated'] += 1
				elif entry == 'unevaluated/protected':
					proposed_route_count["Unevaluated/Protected"] += 1
				elif entry == 'unevaluated/not eligible':
					proposed_route_count["Unevaluated/Not Eligible"] += 1
				elif entry == 'eligible and part of a district':
					proposed_route_count["Eligible and Part of a District"] += 1
		del cursor
	proposed_route_list.append(proposed_route_count)

# Write results to .CSV
fields = ["County", "Eligible", "Eligible and Part of a District", "Eligible/Not Eligible", "Eligible/Unevaluated", "Protected", "Not Eligible", "Not Eligible/Non-Contributing", "Not Eligible/Protected", "Unevaluated", "Unevaluated/Protected", "Unevaluated/Not Eligible"]
write_csv(output_folder, 'S-10_Proposed_Route', fields, proposed_route_list)

# Loop through the alternative routes identifying and counting the amount of features that intersect it
alternative_route_list = []	
for route in routes:
	alternative_route_count = {
	"Route": route,
	"Eligible":0,
	"Eligible/Not Eligible":0,
	"Eligible/Unevaluated":0,
	"Protected":0,
	"Not Eligible":0,
	"Not Eligible/Non-Contributing":0,
	"Not Eligible/Protected":0,
	"Unevaluated/Protected":0,
	"Unevaluated":0,
	"Unevaluated/Not Eligible":0,
	"Eligible and Part of a District":0,
	}
	for feature in feature_list:
		management.SelectLayerByLocation(feature, "INTERSECT", route, '', 'NEW_SELECTION')
		with da.SearchCursor(feature, "NR_Status") as cursor:
			for row in cursor:
				entry = row[0]
				if entry == 'eligible':
					alternative_route_count['Eligible'] += 1
				elif entry == 'eligible/not eligible':
					alternative_route_count["Eligible/Not Eligible"] += 1
				elif entry == 'eligible/unevaluated':
					alternative_route_count["Eligible/Unevaluated"] += 1
				elif entry == 'protected':
					alternative_route_count['Protected'] += 1
				elif entry == 'not eligible':
					alternative_route_count['Not Eligible'] += 1
				elif entry == 'not eligible/non-contributing':
					alternative_route_count["Not Eligible/Non-Contributing"] += 1
				elif entry == 'not eligible/protected':
					alternative_route_count["Not Eligible/Protected"] += 1
				elif entry == 'unevaluated':
					alternative_route_count['Unevaluated'] += 1
				elif entry == 'unevaluated/protected':
					alternative_route_count["Unevaluated/Protected"] += 1
				elif entry == 'unevaluated/not eligible':
					alternative_route_count["Unevaluated/Not Eligible"] += 1
				elif entry == 'eligible and part of a district':
					proposed_route_count["Eligible and Part of a District"] += 1
		del cursor
	alternative_route_list.append(alternative_route_count)

# Write results to .CSV
fields = ["Route", "Eligible", "Eligible and Part of a District", "Eligible/Not Eligible", "Eligible/Unevaluated", "Protected", "Not Eligible", "Not Eligible/Non-Contributing", "Not Eligible/Protected", "Unevaluated", "Unevaluated/Protected", "Unevaluated/Not Eligible"]
write_csv(output_folder, 'S-10_Alternative_Route', fields, alternative_route_list)

''' Perform Same Query For Monitoring Polygon'''

monitoring_poly = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\Survey\2016_BLM_Version.gdb\Monitoring_polygon'
management.MakeFeatureLayer(monitoring_poly, "MP", "DataSource LIKE 'GPS%'")

proposed_route_list = []

for county in counties_list:
	proposed_route_count = {
	"County": "Proposed Route, " + county + " County",
	"Eligible":0,
	"Eligible/Not Eligible":0,
	"Eligible/Unevaluated":0,
	"Protected":0,
	"Not Eligible":0,
	"Not Eligible/Non-Contributing":0,
	"Not Eligible/Protected":0,
	"Unevaluated/Protected":0,
	"Unevaluated":0,
	"Unevaluated/Not Eligible":0,
	"Eligible and Part of a District":0,
	}

	management.SelectLayerByLocation("MP", "INTERSECT", county, '', 'NEW_SELECTION')
	management.SelectLayerByLocation("MP", "INTERSECT", 'Proposed Route', '', 'SUBSET_SELECTION')
	with da.SearchCursor("MP", "NR_Status") as cursor:
		for row in cursor:
			entry = row[0]
			if entry == 'eligible':
				proposed_route_count['Eligible'] += 1
			elif entry == 'eligible/not eligible':
				proposed_route_count["Eligible/Not Eligible"] += 1
			elif entry == 'eligible/unevaluated':
				proposed_route_count["Eligible/Unevaluated"] += 1
			elif entry == 'protected':
				proposed_route_count['Protected'] += 1
			elif entry == 'not eligible':
				proposed_route_count['Not Eligible'] += 1
			elif entry == 'not eligible/non-contributing':
				proposed_route_count["Not Eligible/Non-Contributing"] += 1
			elif entry == 'not eligible/protected':
				proposed_route_count["Not Eligible/Protected"] += 1
			elif entry == 'unevaluated':
				proposed_route_count['Unevaluated'] += 1
			elif entry == 'unevaluated/protected':
				proposed_route_count["Unevaluated/Protected"] += 1
			elif entry == 'unevaluated/not eligible':
				proposed_route_count["Unevaluated/Not Eligible"] += 1
			elif entry == 'eligible and part of a district':
				proposed_route_count["Eligible and Part of a District"] += 1
		del cursor
	proposed_route_list.append(proposed_route_count)

# Write results to .CSV
fields = ["County", "Eligible", "Eligible and Part of a District", "Eligible/Not Eligible", "Eligible/Unevaluated", "Protected", "Not Eligible", "Not Eligible/Non-Contributing", "Not Eligible/Protected", "Unevaluated", "Unevaluated/Protected", "Unevaluated/Not Eligible"]
write_csv(output_folder, 'S-10_Proposed_Route_Class_I_Update', fields, proposed_route_list)

# Loop through the alternative routes identifying and counting the amount of features that intersect it
alternative_route_list = []	
for route in routes:
	alternative_route_count = {
	"Route": route,
	"Eligible":0,
	"Eligible/Not Eligible":0,
	"Eligible/Unevaluated":0,
	"Protected":0,
	"Not Eligible":0,
	"Not Eligible/Non-Contributing":0,
	"Not Eligible/Protected":0,
	"Unevaluated/Protected":0,
	"Unevaluated":0,
	"Unevaluated/Not Eligible":0,
	"Eligible and Part of a District":0,
	}

	management.SelectLayerByLocation("MP", "INTERSECT", route, '', 'NEW_SELECTION')
	with da.SearchCursor("MP", "NR_Status") as cursor:
		for row in cursor:
			entry = row[0]
			if entry == 'eligible':
				alternative_route_count['Eligible'] += 1
			elif entry == 'eligible/not eligible':
				alternative_route_count["Eligible/Not Eligible"] += 1
			elif entry == 'eligible/unevaluated':
				alternative_route_count["Eligible/Unevaluated"] += 1
			elif entry == 'protected':
				alternative_route_count['Protected'] += 1
			elif entry == 'not eligible':
				alternative_route_count['Not Eligible'] += 1
			elif entry == 'not eligible/non-contributing':
				alternative_route_count["Not Eligible/Non-Contributing"] += 1
			elif entry == 'not eligible/protected':
				alternative_route_count["Not Eligible/Protected"] += 1
			elif entry == 'unevaluated':
				alternative_route_count['Unevaluated'] += 1
			elif entry == 'unevaluated/protected':
				alternative_route_count["Unevaluated/Protected"] += 1
			elif entry == 'unevaluated/not eligible':
				alternative_route_count["Unevaluated/Not Eligible"] += 1
			elif entry == 'eligible and part of a district':
				proposed_route_count["Eligible and Part of a District"] += 1
		del cursor
	alternative_route_list.append(alternative_route_count)

# Write results to .CSV
fields = ["Route", "Eligible", "Eligible and Part of a District", "Eligible/Not Eligible", "Eligible/Unevaluated", "Protected", "Not Eligible", "Not Eligible/Non-Contributing", "Not Eligible/Protected", "Unevaluated", "Unevaluated/Protected", "Unevaluated/Not Eligible"]
write_csv(output_folder, 'S-10_Alternative_Route_Class_I_Update', fields, alternative_route_list)
