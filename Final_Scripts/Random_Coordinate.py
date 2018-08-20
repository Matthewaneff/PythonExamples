import arcpy, numpy, os
from arcpy import *
from numpy import random

env.overwriteOutput = "TRUE"

input_feature = GetParameter(0)
(file_path, file_name) = os.path.split(GetParameterAsText(1))
point_num = int(GetParameterAsText(2))
desc = arcpy.Describe(input_feature)
projection = desc.spatialReference

point_feature = management.CreateFeatureclass(file_path, file_name, "POINT", '', '', '', projection)

search_cursor = da.SearchCursor(input_feature, "SHAPE@")
row = search_cursor.next()
extent = row[0].extent

countdown = point_num
array = arcpy.Array()

while countdown > 0:
	poly = row[0]
	point = arcpy.Point()
	point.X = random.uniform(extent.XMin, extent.XMax)
	point.Y = random.uniform(extent.YMin, extent.YMax)
	if point.within(poly):
		array.append(point)
		countdown = countdown - 1

del search_cursor

for item in array:
	with da.InsertCursor(point_feature, ["SHAPE@"]) as cursor:
		cursor.insertRow([item])

del cursor
