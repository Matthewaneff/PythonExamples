import os, sys
from arcpy import *

'''
Similar to Joe's version, but designed as a script tool in the ArcGIS/Catalog
environment.

This script uses the os library to loop through folders that exist in the input folder
provided by the user and collect shapefiles.  It then uses the Describe class to check
the spatial reference system of each file before adding it to the merge list directly,
or reprojecting it as a temporary 'in_memory' file, before adding it to the merge list.
It then merges the list of shapefiles, before clearing the cache of any temporary files
'''

if __name__ == '__main__':

	# Initialize parameters from ArcGIS Script Tool
	inputFolder = GetParameterAsText(0)
	outputFC = GetParameterAsText(1)
	projection = GetParameterAsText(2)

	# Collect all the directories and subdirectories
	folderList = []
	for root, dirs, files in os.walk(inputFolder):			# Loop through the input folder using Walk
		folderList.append(root) 							# Add only directories to the folder list

	# Collect all the shapefiles
	shapefiles = []
	for folder in folderList: 								# Loop through folder list
		for i in os.listdir(folder):						# List files in each folder
			if  i.endswith('.shp'):							# If file has .shp extension, add it to the shapefile folder
				shapefiles.append(os.path.join(folder, i))	

	# Check projections
	mergeList = []
	for shp in shapefiles:
		count = 1
		desc = Describe(shp)
		if desc.spatialReference != projection:
			fields = [str(i.name) for i in ListFields(shp)]
			temp = management.CreateFeatureclass("in_memory", "temp_{}".format(str(count)), desc.shapeType, shp, '', '', projection)
			inscurs = da.InsertCursor(temp, fields)
			with da.SearchCursor(shp, fields) as cursor:
				for row in cursor:
					atts = []
					for i in range(len(fields)):
						row[i] = fields[i]
						atts.append(row[i])
					inscurs.insertRow(atts)
			
			del inscurs
			count += 1
			
		else:
			mergeList.append(shp)

	# Merge datasets
	management.Merge(mergeList, outputFC)
		
	# Clear cache
	for shp in mergeList:									# Loop through merge list
		if os.path.dirname(shp) == 'in_memory':				# If shapefile is stored in memory, delete it
			management.Delete(shp)
