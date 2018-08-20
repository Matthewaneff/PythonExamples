from arcpy import *
import csv, os, sys


def Get_ResourceID():
    '''
	This function uses a search cursor to collect the individual resource
	IDs for every feature in a feature class, and them to an empty list,
	and return that list as an object
	'''

    idList = []

    # Gather Individual Resource IDs
    with da.SearchCursor(lyr, "Resource_ID") as cursor:
        for row in cursor:
            idList.append(row[0])

    return idList


def Get_Attributes(resource_list, intersectFeature, intersectField):
    '''
	This function is designed to collect the desired attributes from a
	dataset that intersects the primary dataset
	'''

    dict_list = []

    for item in resource_list:
        # Isolate feature by selection
        management.SelectLayerByAttribute(lyr, "NEW_SELECTION", "Resource_ID = '{}'".format(item))
        management.SelectLayerByLocation(intersectFeature, "INTERSECT", lyr, '', "NEW_SELECTION")

        dictionary = {'Resource': '{}'.format(item), }
        values = []

        with da.SearchCursor(intersectFeature, intersectField) as cursor:
            for row in cursor:
                values.append(row[0])

        dictionary['Attributes'] = ', '.join(values)
        dict_list.append(dictionary)

    return dict_list


def Update_Attributes(updateField, dList):
    with da.UpdateCursor(lyr, ["Resource_ID", updateField]) as cursor:
        for row in cursor:
            for item in dList:
                if row[0] == item['Resource']:
                    row[1] = item['Attributes']
                    cursor.updateRow(row)

    return


"""
========================================================================
Site_Attribute_Extraction.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
03/21/2017		MF			Created
========================================================================
This script is designed to drastically reduce the amount of working hours
required to gather basic spatial attributes related to the location of 
cultural sites.  A single Point feature class, as is an ID field
for the feature class, and an output feature class are the only required
inputs.  All other input datasets are not required for the script to run.
"""

'''Initialize Parameters'''

inputFeature = GetParameterAsText(0)
inputID = GetParameterAsText(1)
(folder, feature) = os.path.split(GetParameterAsText(2))

desc = Describe(inputFeature)
shapeType = desc.shapeType
spatialRef = desc.spatialReference

'''Gather Datasets'''

spatialJoin = []
spatialJoin_field = []
spatialJoin_column = []

# Define State Dataset
state = GetParameterAsText(3)
state_field = GetParameterAsText(4)
if state != '':
    spatialJoin.append(state)
    spatialJoin_field.append(state_field)
    spatialJoin_column.append('State')

# Define County Dataset
county = GetParameterAsText(5)
county_field = GetParameterAsText(6)
if county != '':
    spatialJoin.append(county)
    spatialJoin_field.append(county_field)
    spatialJoin_column.append('County')

# Define Township/Range Dataset
township = GetParameterAsText(7)
township_field = GetParameterAsText(8)
if township != '':
    spatialJoin.append(township)
    spatialJoin_field.append(township_field)
    spatialJoin_column.append('TwnshpRng')

# Define Section Dataset
sect = GetParameterAsText(9)
sect_field = GetParameterAsText(10)
if sect != '':
    spatialJoin.append(sect)
    spatialJoin_field.append(sect_field)
    spatialJoin_column.append('Section')

# Define Quadrangle Dataset
quad = GetParameterAsText(11)
quad_field = GetParameterAsText(12)
if quad != '':
    spatialJoin.append(quad)
    spatialJoin_field.append(quad_field)
    spatialJoin_column.append('Quad')

'''Script Starts Here'''
if __name__ == '__main__':

    outputFeature = management.CreateFeatureclass(folder, feature, "{}".format(shapeType), '', '', '', spatialRef)
    management.AddField(outputFeature, "Resource_ID", "TEXT")
    [management.AddField(outputFeature, "{}".format(i), "TEXT") for i in spatialJoin_column]
    lyr = management.MakeFeatureLayer(outputFeature, "LYR")

    with da.SearchCursor(inputFeature, ["SHAPE@", inputID]) as cursor:
        for row in cursor:

            # If the row contains a multiple parts...
            if row[0].isMultipart == True:
                array = Array()
                count = row[0].partCount

                # Parse the row into the individaul parts
                for i in range(count):
                    part = Array()

                    # For each  vertice in each part of the row, extract the coordinates
                    for vertice in row[0].getPart(i):
                        point = Point(vertice.X, vertice.Y)
                        part.append(point)

                array.add(part)

                # Use an insert cursor to add all the parts for the row into new feature class
                with da.InsertCursor(outputFeature, ["SHAPE@", "Resource_ID"]) as inscurs:
                    if shapeType == 'Polygon':
                        inscurs.insertRow([Polygon(array), row[1]])
                    elif shapeType == 'Polyline':
                        inscurs.insertRow([Polyline(array), row[1]])
                    elif shapeType == 'Point':
                        inscurs.insertRow([PointGeometry(array), row[1]])
                    elif shapeType == 'Multipoint':
                        inscurs.insertRow([Multipoint(array), row[1]])

            else:
                with da.InsertCursor(outputFeature, ["SHAPE@", "Resource_ID"]) as inscurs:
                    inscurs.insertRow([row[0], row[1]])

    resource_IDs = Get_ResourceID()

    # Loop through Spatial Join Features
    for i in range(len(spatialJoin)):
        a = management.MakeFeatureLayer(spatialJoin[i], "Temp")
        b = spatialJoin_field[i]
        c = spatialJoin_column[i]

        x = Get_Attributes(resource_IDs, a, b)
        Update_Attributes(c, x)

        management.Delete(a)
