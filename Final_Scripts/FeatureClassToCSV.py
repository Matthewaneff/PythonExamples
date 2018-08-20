import os, sys, datetime
import pandas as pd
from arcpy import *

env.overwriteOutput = True

"""
========================================================================
FeatureClassToCSV.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
10/25/2017		MF			Created
10/26/2017      MF          Finalized parameters, export.  Published.
========================================================================
Takes an input feature class or shapefile and exports the attribute table
as a .CSV in a user-defined location
"""

if __name__ == '__main__':

    # Initialize parameters
    inputFeature = GetParameterAsText(0)
    fields = GetParameterAsText(1)
    allFields = GetParameter(2)
    outputLocation = GetParameterAsText(3)

    # Format date and time for the output CSV
    date = datetime.datetime.now().strftime('%Y%m%d')
    name = os.path.basename(inputFeature).split('.')[0]

    # Define 'Fields' list based off boolean option (allFields)
    if allFields == False and fields != '':
        fields = fields.split(';')

    elif allFields == True and fields == '':
        fields = [i.name for i in ListFields(inputFeature)]

    elif allFields == True and fields != '':
        fields = [i.name for i in ListFields(inputFeature)]

    else:
        fields = [i.name for i in ListFields(inputFeature)]

    # Write to Log
    AddMessage("===================================================================")
    sVersionInfo = 'FeatureClassToCSV.py, v20171026'
    AddMessage('FeatureClass to CSV, {}'.format(sVersionInfo))
    AddMessage("")
    AddMessage("Support: mitchell.fyock@tetratech.com, 303-2173724")
    AddMessage("")
    AddMessage("Input Feature: {}".format(inputFeature))
    AddMessage("Output CSV: {}".format(os.path.join(outputLocation, '{}_{}.csv'.format(date, name))))
    AddMessage("===================================================================")

    # Create the list that will hold the dictionaries
    outDict = []

    # Create a search cursor to loop through the inputFeature
    with da.SearchCursor(inputFeature, fields) as cursor:
        for row in cursor:

            # Create a blank dictionary to be populated
            rowDict = {}

            # Use indexes to loop through the inputFeature's fields and populate the dictionary accordingly
            for i in range(len(fields)):
                rowDict['{}'.format(fields[i])] = row[i]

            # Add the dictionary to the dictionary list
            outDict.append(rowDict)

    # Create a dataframe and export it out as a CSV
    df = pd.DataFrame(outDict, columns=fields)
    df.to_csv(os.path.join(outputLocation, '{}_{}.csv'.format(date, name)), columns=fields, index=False)
