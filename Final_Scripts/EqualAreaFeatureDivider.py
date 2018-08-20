from arcpy import *
import os, sys, datetime
env.overwriteOutput = True

"""
========================================================================
EqualAreaFeatureDivider.py
========================================================================
Author: Mitchell Fyock
# ========================================================================
Date			Modifier	Description of Change
07/27/2017		MF			Created
========================================================================
Uses the extent of an input polygon to divide the project area into equal
sections based off a user defined number of rows/columns
"""

inputFeature = GetParameterAsText(0)

divNo = GetParameterAsText(1)
if divNo == '':
    divNo = 6

try:
    divNo = int(divNo)
except ValueError:
    AddError('Number of Rows/Columns Must Be Numeric')
    sys.exit()

outputFeature = GetParameterAsText(2)

clip = GetParameter(3)
if clip == '':
    clip = False

(outputFolder, outputName) = os.path.split(outputFeature)

# Write to Log
d = datetime.datetime.now()
sDate = d.strftime("%Y%m%d")
AddMessage(sDate)
AddMessage("===================================================================")
sVersionInfo = 'EqualAreaFeatureDivider.py, v20170728'
AddMessage('Equal Area Feature Divider, {}'.format(sVersionInfo))
AddMessage("")
AddMessage("Support: mitchell.fyock@tetratech.com, 303-217-3724")
AddMessage("")
AddMessage("Input Feature: {}".format(inputFeature))
AddMessage("Number of Rows/Columns: {}".format(str(divNo)))
AddMessage("Total Number of Cells: {}".format(str(int(divNo ** 2))))
AddMessage("Output Feature: {}".format(outputFeature))
AddMessage("===================================================================")

'''Begin Here'''

desc = Describe(inputFeature)
spatialRef = desc.spatialReference
extent = desc.extent

if clip == False:
    newFeature = management.CreateFeatureclass(outputFolder, outputName, "POLYGON", "", "", "", spatialRef)
else:
    newFeature = management.CreateFeatureclass('in_memory', 'temp', "POLYGON", "", "", "", spatialRef)

xMin = extent.XMin
yMin = extent.YMin
xMax = extent.XMax
yMax = extent.YMax

ySpacing = (yMax - yMin) / divNo
xSpacing = (xMax - xMin) / divNo

inscurs = da.InsertCursor(newFeature, "SHAPE@")

for x in range(divNo):
    for y in range(divNo):
        X = xMin + (x * xSpacing)
        Y = yMin + (y * ySpacing)

        array = Array()

        array.append(Point(X, Y))
        array.append(Point(X, (Y + ySpacing)))
        array.append(Point((X + xSpacing), (Y + ySpacing)))
        array.append(Point((X + xSpacing), Y))

        inscurs.insertRow([Polygon(array)])

if clip == True:
    analysis.Clip(newFeature, inputFeature, outputFeature)
