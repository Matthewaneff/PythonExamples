from arcpy import *
import os, sys, datetime

def convert_unit(lenUnit):
	unit = lenUnit.lower()

	if unit == 'meters':
		unit = 'meter'
	elif unit == 'feet':
		unit = 'foot'

	return unit

"""
========================================================================
STP_Grid.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
06/30/2017		MF			Created
========================================================================
This script creates a grid of STP sites and clips them to the user-defined
input geometry.  The output has three fields: ID, Status, and Result.
Each row in the output feature is provided a incrementing ID
"""

def main():

    inputFeature = GetParameterAsText(0)
    (spacingInterval, spacingUnit) = GetParameterAsText(1).split(' ')
    spacingInterval = float(spacingInterval)
    (outputFolder, outputName) = os.path.split(GetParameterAsText(2))

    desc = Describe(inputFeature)

    # Check Projection and Linear Units
    try:
        linearUnit = convert_unit(spacingUnit)
        linearUnit == desc.spatialReference.linearUnitName.lower()
    except ValueError:
    	AddError('Linear Unit and Projection Unit do not match')
    	AddError('Linear Unit: {} | Projection Unit: {}'.format(spatialRef.linearUnitName.title(), spacingUnit.title()))
    	sys.exit()

    # Check Feature Type
    try:
        desc.shapeType == 'Polygon'
    except ValueError:
        AddError('Input Feature must be Polygon')
        sys.exit()

    # Write to log
    d = datetime.datetime.now()
    sDate = d.strftime("%Y%m%d")
    AddMessage(sDate)
    AddMessage("===================================================================")
    sVersionInfo = 'STP_Grid.py, v20170630'
    AddMessage('STP Grid Generator, {}'.format(sVersionInfo))
    AddMessage("")
    AddMessage("Support: mitchell.fyock@tetratech.com, 303-2173724")
    AddMessage("")
    AddMessage("Input Feature: {}".format(inputFeature))
    AddMessage("Spacing Interval: {} {}".format(str(spacingInterval), spacingUnit))
    AddMessage("Output Feature: {}".format(os.path.join(outputFolder, outputName)))
    AddMessage("===================================================================")

    # Create Emprty Feature
    newFeature = management.CreateFeatureclass(outputFolder,outputName, "Point", '', '', '', desc.spatialReference)
    fields = ['STP_ID', 'STP_Status', 'STP_Result']
    [management.AddField(newFeature, "{}".format(i), "TEXT") for i in fields]

    with da.SearchCursor(inputFeature, "SHAPE@") as cursor:
        count = 1
        for row in cursor:
            Poly = row[0]

            extent = row[0].extent

            xMin = extent.XMin
            yMin = extent.YMin
            xMax = extent.XMax
            yMax = extent.YMax

            xRange = xMax - xMin
            yRange = yMax - yMin

            xInt = int(xRange/spacingInterval) + 1
            yInt = int(yRange/spacingInterval) + 1

            array = Array()

            for x in range(xInt):
                for y in range(yInt):
                    xCoord = xMin + (spacingInterval * x)
                    yCoord = yMin + (spacingInterval * y)
                    point = Point(xCoord, yCoord)
                    array.append(point)

            with da.InsertCursor(newFeature, ["SHAPE@", "STP_ID"]) as inscurs:
                for item in array:
                    if item.within(Poly):
                        inscurs.insertRow([item, "STP_{}".format(count)])
                        count += 1

if __name__ == '__main__':
    main()
