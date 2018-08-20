from arcpy import *
import os

inputFeatures = GetParameter(0)

selectionFeature = management.MakeFeatureLayer(GetParameterAsText(1), "Selection_Layer")

for item in inputFeatures:

    # Check Fields
    fields = [i.name for i in ListFields(item)]
    
    lyr = management.MakeFeatureLayer(item, "Layer")

    if "Page_No" in fields:

        sites = []

        with da.SearchCursor(lyr, "OBJECTID") as cursor:
            for row in cursor:
                sites.append(row[0])

        for site in sites:

            management.SelectLayerByAttribute(lyr, "NEW_SELECTION", "OBJECTID = {}".format(site))
            management.SelectLayerByLocation(selectionFeature, "INTERSECT", lyr, '', "NEW_SELECTION")

            pages = []

            with da.SearchCursor(selectionFeature, "PageNumber") as cursor:
                for row in cursor:
                    pages.append(str(row[0]))

            pages = sorted(pages)

            with da.UpdateCursor(lyr, "Page_No") as cursor:
                for row in cursor:
					try:
						char = ', '.join(pages)

						row[0] = char

						cursor.updateRow(row)
						
					except RuntimeError:
						AddError("OBJECTID {} Contains a Bad Row. Page Extractor is Passing this Row".format(site))
						pass
        
        management.Delete(lyr)

    else:

        AddWarning("{} is missing 'Page_No' field".format(item))
