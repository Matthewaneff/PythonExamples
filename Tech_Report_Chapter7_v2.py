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
Tech_Report_Chapter7
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
01/04/2017		MF			Created
01/16/2017		MF			Added 'write_csv' function to script
========================================================================
"""

output_folder = str(GetParameter(0))

# Survey Footprints
'''The 'surveyed_footprint' feature is comprised of all surveys performed, starting with 2011 through to the present.  THIS IS EVERYTHING THAT HAS BEEN SURVEYED IN THE PAST.'''
'''The 'current_footprint' feature is created by merging the route buffer, access buffer, and work area buffers into a single feature for the current survey year'''
surveyed_footprint = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\Routes\Cultural\B2H_to_6B2H\B2H_to_6B2H_Surveyed_Routes.gdb\Footprint\S_Footprint_B2H_to_6B2H_Dissolve'
management.MakeFeatureLayer(surveyed_footprint, "Surveyed_Footprint")
current_footprint = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\05_January_2017\B2H_Project Features_FASC_20160902.gdb\Footprint\Footprint_Merge_Route_Dissolve_OR'
management.MakeFeatureLayer(current_footprint, "Current_Footprint")

# Clip Features
'''The following lines of code create layers from the different components of the footprint to be used for clipping'''
route_poly = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\05_January_2017\B2H_Project Features_FASC_20160902.gdb\Routes\Routes_250ftBuff_Dissolve_OR'
management.MakeFeatureLayer(route_poly, "Route_Poly")
route_line = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\05_January_2017\B2H_Project Features_FASC_20160902.gdb\Routes\Routes_Dissolve_OR'
management.MakeFeatureLayer(route_line, "Route_Line")
work_area = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\05_January_2017\B2H_Project Features_FASC_20160902.gdb\Features\Features_Route_OR'
management.MakeFeatureLayer(work_area, "Work_Area")
access_line = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\05_January_2017\B2H_Project Features_FASC_20160902.gdb\Access\Access_Route_OR'
management.MakeFeatureLayer(access_line, "Access_Line")
access_poly = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\05_January_2017\B2H_Project Features_FASC_20160902.gdb\Access\Access_100ftBuff_Route_OR'
management.MakeFeatureLayer(access_poly, "Access_Poly")

# Create a list of the features to loop through during the numerical analysis
features = ["Route_Poly", "Route_Line", "Work_Area", "Access_Line", "Access_Poly"]
clip_features = ["Route_Poly_clip", "Route_Line_clip", "Work_Area_clip", "Access_Line_clip", "Access_Poly_clip"]
dissolve_features = ["Route_Poly_dissolve", "Route_Line_dissolve", "Work_Area_dissolve", "Access_Line_dissolve", "Access_Poly_dissolve"]

# Isolate the different linear routes in the footprint and create layers of them
routes = []
with da.SearchCursor("Current_Footprint", "ROUTE") as cursor:
	for row in cursor:
		management.MakeFeatureLayer("Current_Footprint", "{}".format(row[0]), "ROUTE = '{}'".format(row[0]))
		routes.append(row[0])

''' Perform Numerical analysis'''

csv_output_total = []
csv_output_surveyed = []

# Start a loop using the 'routes' list
for route in routes:
	
	# Create a blank dictionary for the route to be populated with the results
	total_dict = {
	'Route':route,
	}
		
	# Identify the total mileage for the access roads, route buffer, and work areas for each route and populate the dictionary accordingly
	for item in features:
		management.SelectLayerByAttribute(item, "ADD_TO_SELECTION", "ROUTE = '{}'".format(route))
	
	with da.SearchCursor("Route_Poly", "Acres") as cursor:
		for row in cursor:
			total_dict['Total Route Acreage'] = row[0]
	
	with da.SearchCursor("Route_Line", 'Miles') as cursor:
		for row in cursor:
			total_dict['Total Route Length'] = row[0]
	
	with da.SearchCursor("Access_Poly", "Acres") as cursor:
		for row in cursor:
			total_dict['Total Access Acreage'] = row[0]
	
	with da.SearchCursor("Access_Line", 'Miles') as cursor:
		for row in cursor:
			total_dict['Total Access Length'] = row[0]

	with da.SearchCursor("Work_Area", "Acres") as cursor:
		for row in cursor:
			total_dict['Total Work Area Acreage'] = row[0]
	
	for item in features:
		management.SelectLayerByAttribute(item, "CLEAR_SELECTION")
		
	csv_output_total.append(total_dict)
		
	# Clip each feature to the 'surveyed_footprint' 
	for item in features:
		x = analysis.Clip(item, "Surveyed_Footprint", "in_memory/{}_clip".format(item))
		desc = arcpy.Describe(x)
		if desc.shapeType == 'Polygon':
			management.CalculateField(x, "Acres", "!shape.geodesicArea@acres!", "PYTHON")
		elif desc.shapeType == 'Polyline':
			management.CalculateField(x, "Miles", "!shape.geodesicLength@miles!", "PYTHON")
		management.MakeFeatureLayer(x, "{}_clip".format(item))
	
	for item in clip_features:
		management.SelectLayerByAttribute(item, "ADD_TO_SELECTION", "ROUTE = '{}'".format(route))
	
	# Create a blank dictionary for the route to be populated with the results
	survey_dict = {
	'Route':route,
	}
	
	# Identify the total mileage for the access roads, route buffer, and work areas for each route THAT WAS SURVEYED and populate the dictionary accordingly
	with da.SearchCursor("Route_Poly_clip", "Acres") as cursor:
		for row in cursor:
			survey_dict['Surveyed Route Acreage'] = row[0]
	
	with da.SearchCursor("Route_Line_clip", 'Miles') as cursor:
		for row in cursor:
			survey_dict['Surveyed Route Length'] = row[0]
	
	with da.SearchCursor("Access_Poly_clip", "Acres") as cursor:
		for row in cursor:
			survey_dict['Surveyed Access Acreage'] = row[0]
	
	with da.SearchCursor("Access_Line_clip", 'Miles') as cursor:
		for row in cursor:
			survey_dict['Surveyed Access Length'] = row[0]
	
	with da.SearchCursor("Work_Area_clip", "Acres") as cursor:
		for row in cursor:
			survey_dict['Surveyed Work Area Acreage'] = row[0]
	
	csv_output_surveyed.append(survey_dict)

#Write the results to .CSVs
fields = ['Route', 'Total Route Acreage', 'Total Route Length', 'Total Access Acreage', 'Total Access Length', 'Total Work Area Acreage']
write_csv(output_folder, 'Chapter_7_Totals_By_Route', fields, csv_output_total)
fields = ['Route', 'Surveyed Route Acreage', 'Surveyed Route Length', 'Surveyed Access Acreage', 'Surveyed Access Length', 'Surveyed Work Area Acreage']
write_csv(output_folder, 'Chapter_7_Totals_By_Route_Surveyed', fields, csv_output_surveyed)

"""
Repeat the process above, with minor alterations
Create a .CSV containing the total amount for the combined access, route, and work areas by dissolving the Clip layers and performing another clipping analysis
"""

for item in features:
	# Identify the shapetype of the feature
	desc = arcpy.Describe(item)
	
	# Perform the dissolve function
	x = management.Dissolve(item, "in_memory/{}_dissolve".format(item))
	
	# Calculate the new metrics for the feature, based on its shapetype
	if desc.shapeType == 'Polygon':
		management.AddField(x, "Acres", "DOUBLE")
		management.CalculateField(x, "Acres", "!shape.geodesicArea@acres!", "PYTHON")
	elif desc.shapeType == 'Polyline':
		management.AddField(x, "Miles", "DOUBLE")
		management.CalculateField(x, "Miles", "!shape.geodesicLength@miles!", "PYTHON")
	management.MakeFeatureLayer(x, "{}_dissolve".format(item))	

# Create a blank dictionary for the route to be populated with the results
total_dissolve_dict = {
'Route': 'Combined Routes',
}
	
# Use a search cursor to populate the output csv with the new metrics
with da.SearchCursor("Route_Poly_dissolve", "Acres") as cursor:
	for row in cursor:
		total_dissolve_dict['Total Route Acreage'] = row[0]

with da.SearchCursor("Route_Line_dissolve", 'Miles') as cursor:
	for row in cursor:
		total_dissolve_dict['Total Route Length'] = row[0]

with da.SearchCursor("Access_Poly_dissolve", "Acres") as cursor:
	for row in cursor:
		total_dissolve_dict['Total Access Acreage'] = row[0]

with da.SearchCursor("Access_Line_dissolve", 'Miles') as cursor:
	for row in cursor:
		total_dissolve_dict['Total Access Length'] = row[0]

with da.SearchCursor("Work_Area_dissolve", "Acres") as cursor:
	for row in cursor:
		total_dissolve_dict['Total Work Area Acreage'] = row[0]
	
# Clip each feature to the 'surveyed_footprint' 
for item in dissolve_features:
	x = analysis.Clip(item, "Surveyed_Footprint", "in_memory/{}_clip".format(item))
	desc = arcpy.Describe(x)
	if desc.shapeType == 'Polygon':
		management.CalculateField(x, "Acres", "!shape.geodesicArea@acres!", "PYTHON")
	elif desc.shapeType == 'Polyline':
		management.CalculateField(x, "Miles", "!shape.geodesicLength@miles!", "PYTHON")
	management.MakeFeatureLayer(x, "{}_clip".format(item))

# Identify the total mileage for the access roads, route buffer, and work areas for each route THAT WAS SURVEYED and populate the dictionary accordingly
surveyed_dissolve_dict = {
'Route': 'Combined Routes'
}
	
with da.SearchCursor("Route_Poly_dissolve_clip", "Acres") as cursor:
	for row in cursor:
		surveyed_dissolve_dict['Surveyed Route Acreage'] = row[0]

with da.SearchCursor("Route_Line_dissolve_clip", 'Miles') as cursor:
	for row in cursor:
		surveyed_dissolve_dict['Surveyed Route Length'] = row[0]

with da.SearchCursor("Access_Poly_dissolve_clip", "Acres") as cursor:
	for row in cursor:
		surveyed_dissolve_dict['Surveyed Access Acreage'] = row[0]

with da.SearchCursor("Access_Line_dissolve_clip", 'Miles') as cursor:
	for row in cursor:
		surveyed_dissolve_dict['Surveyed Access Length'] = row[0]

with da.SearchCursor("Work_Area_dissolve_clip", "Acres") as cursor:
	for row in cursor:
		surveyed_dissolve_dict['Surveyed Work Area Acreage'] = row[0]

fields = ['Route', 'Total Route Acreage', 'Total Route Length', 'Total Access Acreage', 'Total Access Length', 'Total Work Area Acreage']
write_csv(output_folder, 'Chapter_7_Totals_Combined_Routes', fields, total_dissolve_dict)
fields = ['Route', 'Surveyed Route Acreage', 'Surveyed Route Length', 'Surveyed Access Acreage', 'Surveyed Access Length', 'Surveyed Work Area Acreage']
write_csv(output_folder, 'Chapter_7_Totals_Combined_Routes_Surveyed', fields, surveyed_dissolve_dict)
