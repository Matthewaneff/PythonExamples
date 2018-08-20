from arcpy import *
env.overwriteOutput = "TRUE"

# Route datasets
footprint = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\05_January_2017\B2H_Project Features_FASC_20160902.gdb\Footprint\Footprint_Merge_Route_Dissolve_OR'
surveyed_footprint = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\Routes\Cultural\B2H_to_6B2H\B2H_to_6B2H_Surveyed_Routes.gdb\Footprint\S_Footprint_B2H_to_6B2H_Dissolve'

# Query datasets
access = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\05_January_2017\B2H_Project Features_FASC_20160902.gdb\Access\Access'
management.MakeFeatureLayer(access, "Access")
route = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\05_January_2017\B2H_Project Features_FASC_20160902.gdb\Routes\Routes'
management.MakeFeatureLayer(route, "Route")
work_area = r'P:\Boardman to Hemingway Transmission Project\B to H Docs\Cultural Resources\B2H_GIS\Data\TetraTech\ASC_CR_Technical__Report\05_January_2017\B2H_Project Features_FASC_20160902.gdb\Features\Work_Areas'
management.MakeFeatureLayer(work_area, "Work_Area")
features = ["Access", "Route", "Work_Area"]

# Isolate the different routes in the footprint and create layers of them
segments = []
with da.SearchCursor(footprint, "ROUTE") as cursor:
	for row in cursor:
		layer = management.MakeFeatureLayer(footprint, "{}".format(row[0]), "ROUTE = '{}'".format(row[0]))
		segments.append(layer)

selection_features = []
clip_features = []

for segment in segments:
	for feature in features:
		desc = arcpy.Describe(feature)
		if desc.shapeType == 'Polygon':
			x = analysis.Intersect([feature, segment], "in_memory/{}_{}_Intersect".format(str(segment).replace(' ', ''), feature))
			management.CalculateField(x, "ACRES", "!shape.geodesicArea@acres!", "PYTHON")
			y = management.MakeFeatureLayer(x, "{}_{}_Selection".format(str(segment).replace(' ', ''), feature), "ROUTE = '{}'".format(segment))
			selection_features.append(y)
			z = analysis.Clip(y, surveyed_footprint, "in_memory/{}_{}_Clip".format(str(segment).replace(' ', ''), feature))
			management.CalculateField(z, "ACRES", "!shape.geodesicArea@acres!", "PYTHON")
			clip_features.append(z)
			
		elif desc.shapeType == 'Polyline':
			x = analysis.Intersect([feature, segment], "in_memory/{}_{}_Intersect".format(str(segment).replace(' ', ''), feature))
			management.CalculateField(x, "MILES", "!shape.geodesicLength@miles!", "PYTHON")
			y = management.MakeFeatureLayer(x, "{}_{}_Selection".format(str(segment).replace(' ', ''), feature), "ROUTE = '{}'".format(segment))
			selection_features.append(y)
			z = analysis.Clip(y, surveyed_footprint, "in_memory/{}_{}_Clip".format(str(segment).replace(' ', ''), feature))
			management.CalculateField(z, "MILES", "!shape.geodesicLength@miles!", "PYTHON")
			clip_features.append(z)

for item in selection_features:
	count = 0
	desc = arcpy.Describe(item)
	if desc.shapeType == 'Polygon':
		with da.SearchCursor(item, "ACRES") as cursor:
			for row in cursor:
				count += row[0]
	else:
		with da.SearchCursor(item, "MILES") as cursor:
			for row in cursor:
				count += row[0]	
	print(str(item) + ": " + str(count))

print("\n")

for item in clip_features:
	count = 0
	desc = arcpy.Describe(item)
	if desc.shapeType == 'Polygon':
		with da.SearchCursor(item, "ACRES") as cursor:
			for row in cursor:
				count += row[0]
	else:
		with da.SearchCursor(item, "MILES") as cursor:
			for row in cursor:
				count += row[0]	
	print(str(item)[10:] + ": " + str(count))
