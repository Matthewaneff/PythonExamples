import os, sys, datetime
from arcpy import *

d = datetime.datetime.now()
sDate = d.strftime("%m/%d/%Y")

# Collect Inputs
inputFeature = GetParameterAsText(0)
idField = GetParameterAsText(1)
outputFeature = GetParameterAsText(2)



# Create Featureclass
fc = management.CreateFeatureclass(os.path.dirname(outputFeature), os.path.basename(outputFeature), "POLYGON", '', '', '', Describe(inputFeature).spatialReference)

# Add Fields
management.AddField(fc, "SITE_", "TEXT")
management.AddField(fc, "SITE_NAME", "TEXT")
management.AddField(fc, "AGENCY_", "TEXT")
management.AddField(fc, "SHPO_ID", "TEXT")
management.AddField(fc, "DATE", "DATE")
management.AddField(fc, "ACRES", "DOUBLE")
management.AddField(fc, "SITE_TYPE", "TEXT")
management.AddField(fc, "SITE_DESC", "TEXT")
management.AddField(fc, "LINEAR", "SHORT")
management.AddField(fc, "ELIGIBILITY", "TEXT")
management.AddField(fc, "ZONE", "SHORT")
management.AddField(fc, "X", "DOUBLE")
management.AddField(fc, "Y", "DOUBLE")
management.AddField(fc, "COMMENTS", "TEXT")
management.AddField(fc, "SOURCE", "TEXT")
management.AddField(fc, "BND_CMPLT", "TEXT")
management.AddField(fc, "CONF", "TEXT")
management.AddField(fc, "VER", "TEXT")
management.AddField(fc, "AREA", "DOUBLE")
management.AddField(fc, "PERIMETER", "DOUBLE")

featureArray = Array()


# Loop through the inputFeature and extract the shape data
with da.SearchCursor(inputFeature, "SHAPE@") as cursor:
	for row in cursor:
		
		# Identify number of parts in row
		partCount = row[0].partCount
		
		# Create an empty array to add vertices to
		array = Array()
		
		# Loop throug the parts in the row
		for i in range(partCount):
			
			# Add vertices to emtpy array
			for point in row[0].getPart(i):
				array.append(point)
		
		# Add array to featureArray
		featureArray.add(array)

# Create a Polygon geometry object from the featureArray
outputPolygon = Polygon(featureArray)

with da.InsertCursor(fc, ["SHAPE@", "SITE_", "SITE_NAME", "AGENCY_", "SHPO_ID", "DATE", "ACRES", "SITE_TYPE", "SITE_DESC", "LINEAR", "ELIGIBILITY", 
						"ZONE", "X", "Y", "SOURCE", "BND_CMPLT", "CONF", "AREA", "PERIMETER"]) as cursor:
	cursor.insertRow([outputPolygon, 
