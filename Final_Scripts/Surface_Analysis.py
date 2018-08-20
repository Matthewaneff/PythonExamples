from arcpy import *
import os, csv

def write_csv(output_folder, table_name, fields, input_list):
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
Surface Analysis
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
03/09/2017		MF			Created
========================================================================
This script is designed to gather surface data from point features and
export them to a CSV
"""


#~ # Define inputs
inFeature = GetParameter(0)
if inFeature == '':
	inFeature = r'C:\Users\Mitchell.Fyock\Desktop\Projects\ND_Wilton_IV_GPS\GIS\Data\TetraTech\Wilton_IV_Data_Master.gdb\Class_3_Data\Datum'
	
inField = GetParameterAsText(1)
if inField == '':
	inField = 'TempNum'
fields = ["SHAPE@", inField]
	
outputLocation = GetParameterAsText(2)
if outputLocation == '':
	outputLocation = r'C:\Users\Mitchell.Fyock\Desktop\Projects\temp'

dem = GetParameterAsText(3)
#~ if dem == '':
	#~ dem = r'C:\Users\Mitchell.Fyock\Desktop\Projects\ND_Wilton_IV_GPS\GIS\Data\TetraTech\Wilton_IV_Data_Master.gdb\DEM_Mosaic_ft'

slope = GetParameterAsText(4)
#~ if slope == '':
	#~ slope = r'C:\Users\Mitchell.Fyock\Desktop\Projects\ND_Wilton_IV_GPS\GIS\Data\TetraTech\Wilton_IV_Data_Master.gdb\DEM_Slope'
	
aspect = GetParameterAsText(5)
#~ if aspect == '':
	#~ aspect = r'C:\Users\Mitchell.Fyock\Desktop\Projects\ND_Wilton_IV_GPS\GIS\Data\TetraTech\Wilton_IV_Data_Master.gdb\DEM_Aspect'

# Describe input features
desc = Describe(inFeature)
featType = desc.shapeType
spatialRef = desc.spatialReference

# Create a temporary feature class to add gather surface information from
tempFeature = management.CreateFeatureclass("in_memory", "temp", "POINT", '','','', spatialRef)
(temp_path, temp_name) = os.path.split(str(tempFeature))
management.AddField(tempFeature, inField, "TEXT")
doubleFields = ['Elevation', 'Slope', 'Aspect_deg']
[management.AddField(tempFeature, i, "DOUBLE", '', '', 2) for i in doubleFields]
management.AddField(tempFeature, "Aspect", "TEXT")
management.MakeFeatureLayer(tempFeature, "tempFeature")

# Use a Search Cursor and an Insert Cursor to insert new rows into the
# temporary feature class
cursor = da.SearchCursor(inFeature, fields)

coordinates = []
featureID = []

for row in cursor:
	coordinates.append(row[0])
	featureID.append(row[1])
	
del cursor

with da.InsertCursor(tempFeature, fields) as cursor:
	for i in range(len(coordinates)):
		n = featureID[i]
		cursor.insertRow([coordinates[i], n])

# Extract Surface Data to temporary points
surface_rasters = [dem, slope, aspect]
surface_layers = []
for item in surface_rasters:
	(folder, feature) = os.path.split(item)
	layer = sa.ExtractValuesToPoints(tempFeature, item, "in_memory/{}".format(feature), "INTERPOLATE")
	surface_layers.append(management.MakeFeatureLayer(layer, feature))
try:
	for i in range(len(surface_rasters)):
		raster_field = doubleFields[i]
		raster_layer = surface_layers[i]
		management.AddJoin("tempFeature", inField, raster_layer, inField, "KEEP_ALL")
		management.CalculateField("tempFeature", "{}.{}".format(temp_name, raster_field), "!{}.RASTERVALU!".format(raster_layer), "PYTHON")
		management.RemoveJoin("tempFeature")
except ValueError:
	pass

# Convert the aspect bearing to a relative direction	
with da.UpdateCursor(tempFeature, ['Aspect', 'Aspect_deg']) as cursor:
	for row in cursor:
		if row[1] > 0 and row[1] <= 22.5:
			row[0] = 'North'
		elif row[1] > 22.5 and row[1] <= 67.5:
			row[0] = 'Northeast'
		elif row[1] > 67.5 and row[1] <= 112.5:
			row[0] = 'East'		
		elif row[1] > 112.5 and row[1] <= 157.5:
			row[0] = 'Southeast'
		elif row[1] > 157.5 and row[1] <= 202.5:
			row[0] = 'South'
		elif row[1] > 202.5 and row[1] <= 247.5:
			row[0] = 'Southwest'
		elif row[1] > 247.5 and row[1] <= 292.5:
			row[0] = 'West'
		elif row[1] > 247.5 and row[1] <= 292.5:
			row[0] = 'Northwest'
		elif row[1] > 292.5 and row[1] <= 337.5:
			row[0] = 'Northwest'
		elif row[1] > 337.5 and row[1] <= 360:
			row[0] = 'North'
		else:
			row[0] = 'Flat'
			
		# Update row
		cursor.updateRow(row)

management.DeleteField(tempFeature, 'Aspect_deg')

# Use a search cursor to extract the surface data from the temporary
# feature class

dict_list = []
dict_fields = [inField, 'Elevation', 'Slope', 'Aspect']

with da.SearchCursor(tempFeature, dict_fields) as cursor:
	for row in cursor:
		dictionary = {
		'{}'.format(inField):row[0],
		'Elevation':row[1],
		'Slope':row[2],
		'Aspect':row[3],
		}
		dict_list.append(dictionary)


# Write the results of the analysis to a .CSV in the output location
write_csv(outputLocation, "Surface_Analysis", dict_fields, dict_list)
