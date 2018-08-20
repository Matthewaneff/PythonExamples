from arcpy import management, da
import os

input_feature = arcpy.GetParameterAsText(0)
input_table = arcpy.GetParameterAsText(1)
fid_column = arcpy.GetParameterAsText(2)
output_location = arcpy.GetParameterAsText(3)

feature_table = management.MakeTableView(input_feature, "fc_table")
feature_name = os.path.basename(input_feature)

attach_table = management.MakeTableView(input_table, "att_table")
attach_name = os.path.basename(input_table)

management.AddJoin(attach_table, "REL_GLOBALID", feature_table, "GlobalID", "KEEP_ALL")

with da.SearchCursor(attach_table, "{}.{}".format(feature_name, fid_column)) as cursor:
	features = [str(row[0]) for row in cursor]
	


"""
>>> for feature in features:
...     
...     newFolder = os.path.join(r'C:\Users\Mitchell.Fyock\Downloads\20180718_T2B_Veg\Photos', feature)
...     os.mkdir(newFolder)
...     
...     with da.SearchCursor("Field_Delineated_Noxious_Weeds_Point__ATTACH", ["Field_Delineated_Noxious_Weeds_Point.FID", "Field_Delineated_Noxious_Weeds_Point__ATTACH.ATT_NAME", "Field_Delineated_Noxious_Weeds_Point__ATTACH.DATA"]) as cursor:
...         for row in cursor:
...             if str(row[0]) == feature:
...                 with open(os.path.join(newFolder, str(row[1])), 'wb') as f:
...                     f.write(row[2].tobytes())
"""
