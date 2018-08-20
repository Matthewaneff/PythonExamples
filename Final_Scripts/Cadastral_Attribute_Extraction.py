import os, sys, datetime
import pandas as pd
from arcpy import *

def Township_Section(inputDS, inputField, townshipDS, townshipField, sectionDS, sectionField):

    sites = []
    dict_list = []

    with da.SearchCursor(inputDS, inputField) as cursor:
        for row in cursor:
            sites.append(row[0])

    for item in sites:
        management.SelectLayerByAttribute(inputDS, "NEW_SELECTION", "{} = '{}'".format(inputField, item))
        management.SelectLayerByLocation(townshipDS, "INTERSECT", inputDS, '', "NEW_SELECTION")
        twnshp_rng = []

        with da.SearchCursor(townshipDS, townshipField) as cursor:
            for row in cursor:
                twnshp_rng.append(row[0])

        for tr in twnshp_rng:
            section = []
            management.SelectLayerByAttribute(townshipDS, "NEW_SELECTION", "{} = '{}'".format(townshipField, tr))
            management.SelectLayerByLocation(sectionDS, "HAVE_THEIR_CENTER_IN", townshipDS, '', "NEW_SELECTION")
            management.SelectLayerByLocation(sectionDS, "INTERSECT", inputDS, '', "SUBSET_SELECTION")

            with da.SearchCursor(sectionDS, sectionField) as cursor:
                for row in cursor:
                    section.append(row[0])

            for s in section:
                dictionary = {"ID":item, "Township/Range":tr, "Section":s}
                dict_list.append(dictionary)

    return dict_list

def Township_Section_Quarter(inputDS, inputField, townshipDS, townshipField, sectionDS, sectionField, quarterDS, quarterField):

    sites = []
    dict_list = []

    with da.SearchCursor(inputDS, inputField) as cursor:
        for row in cursor:
            sites.append(row[0])

    for item in sites:
        management.SelectLayerByAttribute(inputDS, "NEW_SELECTION", "{} = '{}'".format(inputField, item))
        management.SelectLayerByLocation(townshipDS, "INTERSECT", inputDS, '', "NEW_SELECTION")
        twnshp_rng = []

        with da.SearchCursor(townshipDS, townshipField) as cursor:
            for row in cursor:
                twnshp_rng.append(row[0])

        for tr in twnshp_rng:
            section = []
            management.SelectLayerByAttribute(townshipDS, "NEW_SELECTION", "{} = '{}'".format(townshipField, tr))
            management.SelectLayerByLocation(sectionDS, "HAVE_THEIR_CENTER_IN", townshipDS, '', "NEW_SELECTION")
            management.SelectLayerByLocation(sectionDS, "INTERSECT", inputDS, '', "SUBSET_SELECTION")

            with da.SearchCursor(sectionDS, [sectionField, 'OBJECTID']) as cursor:
                for row in cursor:
                    section.append([row[0], row[1]])

            for s in section:
                quarter = []
                management.SelectLayerByAttribute(sectionDS, "NEW_SELECTION", "OBJECTID = {}".format(s[1]))
                management.SelectLayerByLocation(quarterDS, "HAVE_THEIR_CENTER_IN", sectionDS, '', "NEW_SELECTION")
                management.SelectLayerByLocation(quarterDS, "INTERSECT", inputDS, '', "SUBSET_SELECTION")

                with da.SearchCursor(quarterDS, quarterField) as cursor:
                    for row in cursor:
                        quarter.append(row[0])

                for q in quarter:
                    dictionary = {"ID":item, "Township/Range":tr, "Section":s[0], "Quarter":q}
                    dict_list.append(dictionary)

    return dict_list

"""
========================================================================
Cadastral_Attribute_Extraction.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
10/30/2017 		MF			Created
========================================================================

"""

# Initialize Datasets and Paths
inputDataset = GetParameterAsText(0)
inputDataset_field = GetParameterAsText(1)
township_ds = GetParameterAsText(2)
township_field = GetParameterAsText(3)
section_ds = GetParameterAsText(4)
section_field = GetParameterAsText(5)
quarter_ds = GetParameterAsText(6)
quarter_field = GetParameterAsText(7)
outputName = GetParameterAsText(8).replace(' ', '_')

split = os.path.splitext(outputName)
if split[1] != '.xlsx':
    outputName = outputName + '.xlsx'

outputLocation = GetParameterAsText(9)

management.MakeFeatureLayer(inputDataset, "inputDataset")

if township_ds != '' and section_ds != '' and quarter_ds != '':
    management.MakeFeatureLayer(township_ds, "township")
    management.MakeFeatureLayer(section_ds, "section")
    management.MakeFeatureLayer(quarter_ds, "quarter")

    main = Township_Section_Quarter('inputDataset', inputDataset_field, 'township', township_field, 'section', section_field, 'quarter', quarter_field)

    df = pd.DataFrame(main)
    df.to_excel(os.path.join(outputLocation, outputName), columns=['ID', 'Township/Range', 'Section', 'Quarter'], index=False)

elif township_ds != ''and section_ds != '' and quarter_ds == '':
    management.MakeFeatureLayer(township_ds, "township")
    management.MakeFeatureLayer(section_ds, "section")

    main = Township_Section('inputDataset', inputDataset_field, 'township', township_field, 'section', section_field)

    df = pd.DataFrame(main)
    df.to_excel(os.path.join(outputLocation, outputName), columns=['ID', 'Township/Range', 'Section'], index=False)
