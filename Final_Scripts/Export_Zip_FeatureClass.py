from arcpy import *
import os, sys, zipfile, datetime

env.overwriteOutput = True

def zip_folder(path):

    '''
    This function is designed to zip a folder and its contents
    '''

    z = zipfile.ZipFile(os.path.join(path + '.zip'), 'w')

    for f in os.listdir(path):
        os.chdir(path)
        z.write(os.path.join(f))
    z.close()

    return

"""
========================================================================
Export_Zip_Features.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
06/23/2017		MF			Created
========================================================================
This script is designed to export a feature class and zip the folder it
resides in
"""

date = datetime.datetime.now()
date = datetime.date.isoformat(date).replace('-', '')

inputFeatures = GetParameterAsText(0)
inputFCs = inputFeatures.split(";")
outputName = GetParameterAsText(1).replace(' ','_')
outputLocation = GetParameterAsText(2)

if __name__ == '__main__':
    out = os.path.join(outputLocation, date + '_' + outputName)
    os.mkdir(out)

    # Iterate through inputFeatures list
    for item in inputFCs:

        # Clean the input datasets (this is referring to ValueTables in arcpy)
        item = item.strip("'")

        conversion.FeatureClassToShapefile(item, out)

    zip_folder(out)
