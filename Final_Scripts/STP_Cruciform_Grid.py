from arcpy import *
import os, sys, datetime

def convert_unit(lenUnit):
	unit = lenUnit.lower()

	if unit == 'meters':
		unit = 'meter'
	elif unit == 'feet':
		unit = 'foot'

	return unit

def get_centroid(feature, f):

    '''Returns a list of coordinates'''

    coordList = []

    with da.SearchCursor(feature, ["SHAPE@", f]) as cursor:
        for row in cursor:
            centroid = row[0].centroid
            point = [centroid.X, centroid.Y]
            coordList.append([point, row[1]])
	
    return coordList

def get_cruciform(coordinateList):

    '''Uses an existing list to create four new coordinates and add them to a new list'''

    coordList = []

    for item in coordinateList:
        x = item[0][0]
        y = item[0][1]
        xy_ID = item[1]

        coordList.append([Point((x + 20), y), str(xy_ID + '_E')])
        coordList.append([Point((x - 20), y), str(xy_ID + '_W')])
        coordList.append([Point(x, y + 20), str(xy_ID + '_N')])
        coordList.append([Point(x, y - 20), str(xy_ID + '_S')])
        coordList.append([Point(x,y), str(xy_ID + '_C')])

    return coordList

def insert_XY(coordinateList, feature):

    '''
    Inserts coordinates contained in list
    '''

    with da.InsertCursor(feature, ["SHAPE@", "STP_ID"]) as cursor:
        for item in coordinateList:
            point = PointGeometry(item[0])
            cursor.insertRow([point, item[1]])

    return

"""
========================================================================
STP_Cruciform_Grid.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
06/30/2017		MF			Created
========================================================================
This script can either create a new STP file, or append new STPs to an
existing file in the 'Cruciform' shape (20 units of measurement in the
four cardinal directions).
"""

inputFeature = GetParameterAsText(0)
desc = Describe(inputFeature)
try:
    desc.shapeType == 'Point'
except ValueError:
    AddError('Input Feature type is not a Point')
    sys.exit()

idField = GetParameterAsText(1)

fields = [i.name for i in ListFields(inputFeature)]
if idField not in fields:
    AddError('Field does not exist in input feature')
    sys.exit()

newFeature = GetParameterAsText(2)
appendFeature = GetParameterAsText(3)

# Write to log
d = datetime.datetime.now()
sDate = d.strftime("%Y%m%d")
AddMessage(sDate)
AddMessage("===================================================================")
sVersionInfo = 'STP_Cruciform_Grid.py, v20170630'
AddMessage('STP Grid Generator, {}'.format(sVersionInfo))
AddMessage("")
AddMessage("Support: mitchell.fyock@tetratech.com, 303-2173724")
AddMessage("")
AddMessage("Input Feature: {}".format(inputFeature))
if newFeature != '':
	AddMessage("Output Feature: {}".format(newFeature))
elif newFeature == '' and appendFeature != '':
	AddMessage("Output Feature: {}".format(appendFeature))
AddMessage("===================================================================")

# Begin Here

if newFeature != '' and appendFeature == '':

    # Create empty feature class and add fields
    (outputFolder, outputName) = os.path.split(newFeature)
    newFeature = management.CreateFeatureclass(outputFolder,outputName, "Point", '', '', '', desc.spatialReference)
    fields = ['STP_ID', 'STP_Status', 'STP_Result']
    [management.AddField(newFeature, "{}".format(i), "TEXT") for i in fields]

    coords = get_centroid(inputFeature, idField)

    coords = get_cruciform(coords)

    insert_XY(coords, newFeature)

elif newFeature == '' and appendFeature != '':

    fields = [i.name for i in ListFields(appendFeature)]
    if idField not in fields:
        AddError('Field does not exist in input feature')
        sys.exit()

    coords = get_centroid(inputFeature, idField)

    coords = get_cruciform(coords)

    insert_XY(coords, appendFeature)

elif newFeature == '' and appendFeature == '':
    AddError('No output feature provided')
    sys.exit()
