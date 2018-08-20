from arcpy import *
import os

inputFeatures = GetParameter(0)

selectionFeature = management.MakeFeatureLayer(GetParameterAsText(1), "Selection_Layer")

for item in inputFeatures:

    # Check Fields
    fields = [i.name for i in ListFields(item)]
    
    lyr = management.MakeFeatureLayer(item, "Layer")

    if "County" in fields:

        sites = []

        with da.SearchCursor(lyr, "OBJECTID") as cursor:
            for row in cursor:
                sites.append(row[0])

        for site in sites:

            management.SelectLayerByAttribute(lyr, "NEW_SELECTION", "OBJECTID = {}".format(site))
            management.SelectLayerByLocation(selectionFeature, "INTERSECT", lyr, '', "NEW_SELECTION")

            counties = []

            with da.SearchCursor(selectionFeature, "NAME") as cursor:
                for row in cursor:
                    counties.append(str(row[0]))

            counties = sorted(counties)

            with da.UpdateCursor(lyr, "County") as cursor:
                for row in cursor:
					try:
						char = ', '.join(counties)

						row[0] = char

						cursor.updateRow(row)
						
					except RuntimeError:
						AddError("OBJECTID {} Contains a Bad Row. Page Extractor is Passing this Row".format(site))
						pass
        
        management.Delete(lyr)

    else:

        AddWarning("{} is missing 'Page_No' field".format(item))
