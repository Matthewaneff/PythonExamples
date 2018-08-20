from arcpy import *
import sys, datetime, os
import pandas as pd

"""
========================================================================
TR_S_Q_QQ_Extraction.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
08/31/2017 		MF			Created
========================================================================
For use with BLM Geocommunicator Geodatabases only.  Performs a series of
Select By Attribute and Select By Location functions to identify the different
PLSS Township/Range, Sections, Quarters, and Quarter-Quarters that intersect
the user-provided input dataset.
"""

# Initialize Datasets and Paths
inputDataset = GetParameterAsText(0)
inputDataset_field = GetParameterAsText(1)
township_ds = GetParameterAsText(2)
section_ds = GetParameterAsText(3)
quarter_ds = GetParameterAsText(4)
qq_ds = GetParameterAsText(5)
outputName = GetParameterAsText(6).replace(' ', '_')
split = os.path.splitext(outputName)
if split[1] != '.xlsx':
    outputName = outputName + '.xlsx'

outputLocation = GetParameterAsText(7)

management.MakeFeatureLayer(inputDataset, "inputDataset")
management.MakeFeatureLayer(township_ds, "PLSSTownship")
management.MakeFeatureLayer(section_ds, "PLSSReferenceGrid")
management.MakeFeatureLayer(quarter_ds, "PLSSQuarterReference")
management.MakeFeatureLayer(qq_ds, "PLSSSecondDivision")

# Write to Log
AddMessage(' ')
AddMessage("===================================================================")
sVersionInfo = 'TR_S_Q_QQ_Extraction.py, v20170831'
AddMessage('PLSS Attribute Extraction, {}'.format(sVersionInfo))
AddMessage("")
AddMessage("Support: mitchell.fyock@tetratech.com, 303-217-3724")
AddMessage("")
AddMessage("Input Dataset: {}".format(inputDataset))
AddMessage("Output Location: {}".format(outputLocation))
AddMessage("Output Name: {}".format(outputName))
AddMessage("===================================================================")
AddMessage(' ')

if __name__ == '__main__':

    sites = []
    dict_list = []

    with da.SearchCursor(inputDataset, inputDataset_field) as cursor:
        for row in cursor:
            sites.append(row[0])

    for item in sites:
        management.SelectLayerByAttribute("inputDataset", "NEW_SELECTION", "{} = '{}'".format(inputDataset_field, item))
        management.SelectLayerByLocation("PLSSTownship", "INTERSECT", "inputDataset", '', "NEW_SELECTION")
        twnshp_rng = []

        with da.SearchCursor("PLSSTownship", "TWNSHPLAB") as cursor:
            for row in cursor:
                twnshp_rng.append(row[0])

        for tr in twnshp_rng:
            section = []
            management.SelectLayerByAttribute("PLSSTownship", "NEW_SELECTION", "TWNSHPLAB = '{}'".format(tr))
            management.SelectLayerByLocation("PLSSReferenceGrid", "HAVE_THEIR_CENTER_IN", "PLSSTownship", '', "NEW_SELECTION")
            management.SelectLayerByLocation("PLSSReferenceGrid", "INTERSECT", "inputDataset", '', "SUBSET_SELECTION")

            with da.SearchCursor("PLSSReferenceGrid", ["REFGRIDNOM", "OBJECTID"]) as cursor:
                for row in cursor:
                    section.append([row[0], row[1]])

            for s in section:
                quarter = []
                management.SelectLayerByAttribute('PLSSReferenceGrid', "NEW_SELECTION", "OBJECTID = {}".format(s[1]))
                management.SelectLayerByLocation('PLSSQuarterReference', "HAVE_THEIR_CENTER_IN", "PLSSReferenceGrid", '', "NEW_SELECTION")
                management.SelectLayerByLocation('PLSSQuarterReference', "INTERSECT", "inputDataset", '', "SUBSET_SELECTION")

                with da.SearchCursor("PLSSQuarterReference", ["QSECTION", "OBJECTID"]) as cursor:
                    for row in cursor:
                        quarter.append([row[0], row[1]])

                for q in quarter:
                    qq = []
                    management.SelectLayerByAttribute("PLSSQuarterReference", "New_Selection", "OBJECTID = {}".format(q[1]))
                    management.SelectLayerByLocation('PLSSSecondDivision', "HAVE_THEIR_CENTER_IN", "PLSSQuarterReference", '', "NEW_SELECTION")
                    management.SelectLayerByLocation('PLSSSecondDivision', "INTERSECT", "inputDataset", '', "SUBSET_SELECTION")

                    with da.SearchCursor('PLSSSecondDivision', "SECDIVLAB") as cursor:
                        for row in cursor:
                            qq.append(row[0])

                    dict = {"ID":item, "Township/Range":tr, "Section":s[0], "Quarter":q[0], 'Quarter-Quarter':', '.join(qq)}
                    dict_list.append(dict)

    df = pd.DataFrame(dict_list)
    df.to_excel(os.path.join(outputLocation, outputName), cols=['ID', 'Township/Range', 'Section', 'Quarter', 'Quarter-Quarter'], index=False)
