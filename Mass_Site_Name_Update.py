from arcpy import *
import pandas as pd
import sys, os, datetime

"""
========================================================================
Mass_Site_Name_Update.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
10/02/2017		MF			Created
========================================================================
Cycles through a user-specified feature dataset renaming site name attributes
stored in feature classes using a .csv that contains the old and new names
"""

inputWorkspace = GetParameterAsText(0)
gdb, ds = os.path.split(inputWorkspace)

csvFile = GetParameterAsText(1)

oldNamesHeader = GetParameterAsText(2)
newNamesHeader = GetParameterAsText(3)

df = pd.DataFrame(pd.read_csv(csvFile))

oldNames = [i for i in df['{}'.format(oldNamesHeader)]]
newNames = [i for i in df['{}'.format(newNamesHeader)]]

if len(oldNames) != len(newNames):
    AddError('Please Check Table Entries...')
    sys.exit()

env.workspace = gdb

for item in ListFeatureClasses('', '', ds):

    fields = [i.name for i in ListFields(item)]

    if oldNamesHeader in fields and newNamesHeader in fields:

        rowCount = management.GetCount(item)

        if int(rowCount.getOuput(0)) > 0:

            AddMessage('Updating {} Feature Class...')

            for i in range(len(oldNames)):
                tempNum = oldNames[i]
                siteNum = newNames[i]

                with da.UpdateCursor(item, [oldNamesHeader, newNamesHeader]) as cursor:
                    for row in cursor:

                        if row[0] == tempNum:
                            row[1] = siteNum

                        cursor.updateRow(row)
