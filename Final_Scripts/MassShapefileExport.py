from arcpy import *
import os, sys, zipfile
import pandas as pd

"""
========================================================================
MassShapefileExport.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
06/22/2017		MF			Created
========================================================================
This script has been designed for the Boardman to Hemmingway project.
It performs a simple Select By Attribute function, and then creates a folder with
the queried site name, stores a shapefile in it, and then compresses the folder
as a .ZIP
"""

env.overwriteOutput = True

inputFeatures = GetParameterAsText(0)
inputFCs = inputFeatures.split(';')

inputExcel = GetParameterAsText(1)
outputLocation = GetParameterAsText(2)

df = pd.DataFrame(pd.read_excel(inputExcel, "Sheet1"))

sites = [i for i in df['TempNum']]

for i in sites:
    os.mkdir(os.path.join(outputLocation, i))

# Iterate through inputFeatures list
for item in inputFCs:

    # Clean the input datasets (this is referring to ValueTables in arcpy)
    item = item.strip("'")
    name = os.path.basename(item)

    # Convert Feature Class to Layer
    lyr = management.MakeFeatureLayer(item, "{}".format(name))

    fields = [i.name for i in ListFields(item)]

    # Select each site from the feautre class and export it as a single shapefile
    for site in sites:
        if 'FeatArtType' not in fields:
            management.SelectLayerByAttribute(lyr, "NEW_SELECTION", "TempNumber = '{}'".format(site))
            conversion.FeatureClassToShapefile(lyr, os.path.join(outputLocation, "{}".format(site)))

        else:
            management.SelectLayerByAttribute(lyr, "NEW_SELECTION", "TempNumber = '{}' AND FeatArtType = 'site datum'".format(site))
            conversion.FeatureClassToShapefile(lyr, os.path.join(outputLocation, "{}".format(site)))

path = outputLocation

# Compress Contents of Directory to .ZIP files
for folder in os.listdir(path):
    # For each folder in the Directory, create a new .zip folder
    z = zipfile.ZipFile(os.path.join(path, folder + '.zip'), 'w')

    # For each file in a each directory, add it to the corresponding .zip folder
    for f in os.listdir(os.path.join(path, folder)):
        os.chdir(os.path.join(path, folder))
        z.write(os.path.join(f))
    z.close()
