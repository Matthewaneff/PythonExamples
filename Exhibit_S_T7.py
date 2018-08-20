import os, csv
from arcpy import *
env.overwriteOutput = "TRUE"

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
Exhibit_S_T7
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


output_folder = str(GetParameter(0))

# Footprints
surveyed_footprint = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\Routes\Cultural\B2H_to_6B2H\B2H_to_6B2H_Surveyed_Routes.gdb\Footprint\S_Footprint_B2H_to_6B2H_Dissolve'
# Routes
route = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\Application_for_Site_Certification\Exhibit_S_Cultural_Resources\06.ODOE pASC_Jan2017\B2H_Project Features_FASC_20160902.gdb\Routes\Routes_Dissolve'
management.MakeFeatureLayer(route, "Routes")
# Counties
county = r'G:\Cultural Resources\GIS_Library\UnitedStates\Census_2013\tl_2013_us_county\tl_2013_us_county.shp'
management.MakeFeatureLayer(county, "Counties", "STATEFP = '41' AND NAME IN ('Baker', 'Umatilla', 'Malheur', 'Union', 'Morrow')")

# Isolate the different routes in the footprint and create layers of them
routes = []
with da.SearchCursor("Routes", ["FEATURE", "ROUTE"]) as cursor:
	for row in cursor:
		if row[0] != 'Proposed Route':
			management.MakeFeatureLayer("Routes", "{}".format(row[1]), "ROUTE = '{}'".format(row[1]))
			routes.append(row[1])
			
management.MakeFeatureLayer("Routes", "Proposed_Route", "ROUTE = 'Proposed Route'")

# Isolate the different counties and create layers from them
counties = []
with da.SearchCursor("Counties", "NAME") as cursor:
	for row in cursor:
		management.MakeFeatureLayer(county, "{}".format(row[0]), "NAME = '{}'".format(row[0]))
		counties.append(row[0])

''' Perform Numerical analysis'''
proposed_route_list = []
alternative_route_list = []

for county in counties:
	# Create a blank dictionary
	county_dict = {
	"County": "Proposed Route, " + county + " County",
	"Total":0,
	"Surveyed":0,
	"Percent Complete":0,
	}
	
	# Loop through Route feature class and populate the dictionary with the total mileage
	total_mileage = 0
	management.SelectLayerByAttribute("Proposed_Route", "NEW_SELECTION", "COUNTY = '{}'".format(county))
	with da.SearchCursor("Proposed_Route", "MILES") as cursor:
		for row in cursor:
			county_dict['Total'] += row[0]
			total_mileage += row[0]
	del cursor
	
	# Clip route by what has been surveyed and populate the table accordingly
	clip = analysis.Clip("Proposed_Route", surveyed_footprint, "in_memory/PR_{}_Clip".format(county))
	management.CalculateField(clip, "MILES", "!shape.geodesicLength@miles!", "PYTHON")
	surveyed_mileage = 0
	with da.SearchCursor(clip, "MILES") as cursor:
		for row in cursor:
			county_dict['Surveyed'] += row[0]
			surveyed_mileage += row[0]
	
	county_dict['Percent Complete'] += (surveyed_mileage/total_mileage)
	del cursor
	
	# Add the dictionary to the dictionary list
	proposed_route_list.append(county_dict)

# Write results to a .CSV
fields = ['County', 'Total', 'Surveyed', 'Percent Complete']
write_csv(output_folder, 'S-7_Proposed_Route', fields,  proposed_route_list)

for route in routes:
	# Create a blank dictionary
	county_dict = {
	"Route": route,
	"Total":0,
	"Surveyed":0,
	"Percent Complete":0,
	}

	# Loop through Route feature class and populate the dictionary with the total mileage	
	total_mileage = 0
	with da.SearchCursor(route, "MILES") as cursor:
		for row in cursor:
			county_dict['Total'] += row[0]
			total_mileage += row[0]
	del cursor
	
	# Clip route by what has been surveyed and populate the table accordingly
	clip = analysis.Clip(route, surveyed_footprint, "in_memory/{}__Clip".format(route.replace(' ','')))
	management.CalculateField(clip, "MILES", "!shape.geodesicLength@miles!", "PYTHON")
	surveyed_mileage = 0
	with da.SearchCursor(clip, "MILES") as cursor:
		for row in cursor:
			county_dict['Surveyed'] += row[0]
			surveyed_mileage += row[0]
	
	county_dict['Percent Complete'] += (surveyed_mileage/total_mileage)
	del cursor

	# Add the dictionary to the dictionary list
	alternative_route_list.append(county_dict)

# Write results to a .CSV
fields = ['Route', 'Total', 'Surveyed', 'Percent Complete']
write_csv(output_folder, 'S-7_Alternative_Route', fields, alternative_route_list)
