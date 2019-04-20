import os, sys, datetime
from arcpy import *

"""
========================================================================
Project_Initializon.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
01/04/2017		MF			Created
08/29/2017		MF			Edited Class III dataset items. Increased functionality allowing user to select desired projection
09/01/2017		MF			Rerouted filepaths to network drive.
12/19/2017		MF			Removed DEM Creator
========================================================================
This script is designed to create a basic, standardized project folder
with a geodatabase that contains all feature datasets, feature classes,
and domains required.
"""

# Assign user inputs to variables
project_name = GetParameterAsText(0)
if project_name == '':
	AddError('Please provide project name.')
	sys.exit()

input_dataset = GetParameter(1)
projection = GetParameterAsText(2)
output_location = GetParameterAsText(3)

# Write to Log
AddMessage(' ')
AddMessage("===================================================================")
sVersionInfo = 'Project_Initialization.py, v20170901'
AddMessage('Project Initialization, {}'.format(sVersionInfo))
AddMessage("")
AddMessage("Support: mitchell.fyock@tetratech.com, 303-217-3724")
AddMessage("")
AddMessage("Project Name: {}".format(project_name))
AddMessage("Output Location: {}".format(output_location))
AddMessage("===================================================================")
AddMessage(" ")

'''Begin Here'''

# Define Domain Files
domains = [
r'\\tts232fs1.TT.LOCAL\GROUPS\Cultural Resources\GIS_Library\Tools\Domains\ArchPot.txt',
r'\\tts232fs1.TT.LOCAL\GROUPS\Cultural Resources\GIS_Library\Tools\Domains\ShovProb.txt',
r'\\tts232fs1.TT.LOCAL\GROUPS\Cultural Resources\GIS_Library\Tools\Domains\SurfaceVis.txt',
r'\\tts232fs1.TT.LOCAL\GROUPS\Cultural Resources\GIS_Library\Tools\Domains\YesNo.txt',
r'\\tts232fs1.TT.LOCAL\GROUPS\Cultural Resources\GIS_Library\Tools\Domains\CardinalDir.txt',
r'\\tts232fs1.TT.LOCAL\GROUPS\Cultural Resources\GIS_Library\Tools\Domains\FeaturePoint.txt',
r'\\tts232fs1.TT.LOCAL\GROUPS\Cultural Resources\GIS_Library\Tools\Domains\FeaturePolygon.txt',
r'\\tts232fs1.TT.LOCAL\GROUPS\Cultural Resources\GIS_Library\Tools\Domains\FeatureLine.txt',
r'\\tts232fs1.TT.LOCAL\GROUPS\Cultural Resources\GIS_Library\Tools\Domains\HistoricArtifact.txt',
r'\\tts232fs1.TT.LOCAL\GROUPS\Cultural Resources\GIS_Library\Tools\Domains\PrehistoricArtifact.txt',
r'\\tts232fs1.TT.LOCAL\GROUPS\Cultural Resources\GIS_Library\Tools\Domains\Affiliation.txt',
r'\\tts232fs1.TT.LOCAL\GROUPS\Cultural Resources\GIS_Library\Tools\Domains\SiteType.txt',
r'\\tts232fs1.TT.LOCAL\GROUPS\Cultural Resources\GIS_Library\Tools\Domains\IsoType.txt',
r'\\tts232fs1.TT.LOCAL\GROUPS\Cultural Resources\GIS_Library\Tools\Domains\LandClass.txt',
r'\\tts232fs1.TT.LOCAL\GROUPS\Cultural Resources\GIS_Library\Tools\Domains\STP_Status.txt',
r'\\tts232fs1.TT.LOCAL\GROUPS\Cultural Resources\GIS_Library\Tools\Domains\STP_Result.txt',
r'\\tts232fs1.TT.LOCAL\GROUPS\Cultural Resources\GIS_Library\Tools\Domains\SurveyStatus.txt',
]

for i in domains:
	if os.path.exists(i) == False:
		domains.remove(i)

survey_features = ["Point", "Polyline", "Polygon"]

# Define primary datasets
us_state_complete = r"\\tts232fs1.TT.LOCAL\GROUPS\Cultural Resources\GIS_Library\UnitedStates\Census_2013\tl_2013_us_state\tl_2013_us_state.shp"
if os.path.exists(us_state_complete) == True:
	management.MakeFeatureLayer(us_state_complete, "US_State_Complete")
else:
	AddError('State Dataset Cannot Be Located')
	sys.exit()

us_county_complete = r"\\tts232fs1.TT.LOCAL\GROUPS\Cultural Resources\GIS_Library\UnitedStates\Census_2013\tl_2013_us_county\tl_2013_us_county.shp"
if os.path.exists(us_county_complete) == True:
	management.MakeFeatureLayer(us_county_complete, "US_County_Complete")
else:
	AddError('County Dataset Cannot Be Located')
	sys.exit()

# Identify State Abbreviation
management.SelectLayerByLocation("US_State_Complete", "INTERSECT", input_dataset)
management.MakeFeatureLayer("US_State_Complete", "State")
with da.SearchCursor("State", "STUSPS") as cursor:
	for row in cursor:
		state_abbrev = row[0]

management.Delete("State")
project_name = state_abbrev + "_" + project_name.replace(' ', '_')

# Create Folder Structure
AddMessage("Building Folder Structure...")

os.mkdir(os.path.join(output_location, project_name))
root = os.path.join(output_location, project_name)

os.mkdir(os.path.join(root, "GIS"))
os.mkdir(os.path.join(root, "Deliverables"))
os.mkdir(os.path.join(root, "GIS", "Data"))
os.mkdir(os.path.join(root, "GIS", "Data", "Consult"))
os.mkdir(os.path.join(root, "GIS", "Data", "Layers"))
os.mkdir(os.path.join(root, "GIS", "Data", "Raster"))
os.mkdir(os.path.join(root, "GIS", "Data", "TetraTech"))
os.mkdir(os.path.join(root, "GIS", "Data", "TetraTech", "Collector"))
os.mkdir(os.path.join(root, "GIS", "Data", "TetraTech", "Trimble"))
os.mkdir(os.path.join(root, "GIS", "Layouts"))
os.mkdir(os.path.join(root, "GIS", "Layouts", "Collector"))
os.mkdir(os.path.join(root, "GIS", "Maps"))
os.mkdir(os.path.join(root, "GIS", "Maps", "Sketch_Maps"))
os.mkdir(os.path.join(root, "GIS", "Maps", "Location_Maps"))

# Create GDB and Feature Datasets
AddMessage("Creating Geodatabase...")

gdb_name = project_name.title() + "_Master.gdb"
management.CreateFileGDB(os.path.join(root, "GIS", "Data", "TetraTech"), gdb_name)
gdb = r'{}\GIS\Data\TetraTech\{}'.format(root, gdb_name)

# Control Projection of Input Dataset
if projection != '':
	temp = management.Project(input_dataset, os.path.join(gdb, 'temp'), projection)
	desc = Describe(temp)
	spatial_ref = desc.spatialReference
	management.Delete(temp)
	del temp

else:
	desc = Describe(input_dataset)
	spatial_ref  = desc.spatialReference

featureDatasets = ["Class_I_Data", "Project_Features", "Class_III_Data", "Survey_Notes", "PLSS", "Transportation", "Hydrology", "Political_Boundaries", "Microsite", "STP"]
for item in featureDatasets:
	management.CreateFeatureDataset(gdb, item, spatial_ref)

# Add Domains to GDB
for item in domains:
	domain_object = os.path.basename(item[:-4])
	management.TableToDomain(item, "Code", "Description", gdb, domain_object)

# Select and export counties based on project
management.SelectLayerByLocation("US_County_Complete", "INTERSECT", input_dataset)
management.SelectLayerByLocation("US_State_Complete", "INTERSECT", input_dataset)
state_selection = management.MakeFeatureLayer("US_State_Complete", "State_Boundary")
county_selection = management.MakeFeatureLayer("US_County_Complete", "Project Counties")
conversion.FeatureClassToFeatureClass(state_selection, gdb, "Political_Boundaries\State_Boundary")
conversion.FeatureClassToFeatureClass(county_selection, gdb, "Political_Boundaries\Project_Counties")

# Add 'Survey_Notes' Feature Class to 'Survey_Data' Feature Dataset
for item in survey_features:
	# Create new Survey Note features and add fields to them
	new_feature = management.CreateFeatureclass(gdb, "Survey_Notes\Survey_{}".format(item), "{}".format(item), '','','', spatial_ref)

# Create Empty Class III Datasets
AddMessage("Creating Feature Datasets...")

datum = management.CreateFeatureclass(gdb, 'Class_III_Data\Datum', 'POINT', '', '', '', spatial_ref)
isolate = management.CreateFeatureclass(gdb, 'Class_III_Data\Isolate', 'POINT', '', '', '', spatial_ref)
featpoint = management.CreateFeatureclass(gdb, 'Class_III_Data\FeaturePoint', 'POINT', '', '', '', spatial_ref)
hist_art = management.CreateFeatureclass(gdb, 'Class_III_Data\HistoricArtifact', 'POINT', '', '', '', spatial_ref)
prehist_art = management.CreateFeatureclass(gdb, 'Class_III_Data\PrehistoricArtifact', 'POINT', '', '', '', spatial_ref)
point = management.CreateFeatureclass(gdb, 'Class_III_Data\Point', 'POINT', '', '', '', spatial_ref)
featline = management.CreateFeatureclass(gdb, 'Class_III_Data\FeatureLine', 'POLYLINE', '', '', '', spatial_ref)
line = management.CreateFeatureclass(gdb, 'Class_III_Data\Line', 'POLYLINE', '', '', '', spatial_ref)
featpoly = management.CreateFeatureclass(gdb, 'Class_III_Data\FeaturePoly', 'POLYGON', '', '', '', spatial_ref)
poly = management.CreateFeatureclass(gdb, 'Class_III_Data\Polygon', 'POLYGON', '', '', '', spatial_ref)
site_bound = management.CreateFeatureclass(gdb, 'Class_III_Data\SiteBoundary', 'POLYGON', '', '', '', spatial_ref)

[management.AddField(datum, i, "TEXT") for i in ['TempNum', 'SmithNum', 'Affiliation', 'SiteType', 'Comment']]
[management.AddField(isolate, i, "TEXT") for i in ['IsoNum', 'SmithNum', 'Affiliation', 'IsoType', 'Comment']]
[management.AddField(site_bound, i, "TEXT") for i in ['TempNum', "SmithNum", "Comment"]]

for d in [featpoint, featline, featpoly]:
	[management.AddField(d, i, "TEXT") for i in ['TempNum', 'SmithNum', 'Affiliation', 'F_Type', 'F_Num', 'Comment']]

for d in [hist_art, prehist_art]:
	[management.AddField(d, i, "TEXT") for i in ['TempNum', 'SmithNum', 'FS_Type', 'FS_Num', 'Comment']]

for d in [point, line, poly]:
	management.AddField(d, "Comment", "TEXT")

# Assign Domains to Features
AddMessage("Assigning Domains...")

for i in [datum, isolate, featline, featpoint, featpoly]:
	management.AssignDomainToField(i, "Affiliation", "Affiliation")

management.AssignDomainToField(datum, "SiteType", "SiteType")
management.AssignDomainToField(isolate, "IsoType", "IsoType")
management.AssignDomainToField(featline, "F_Type", "FeatureLine")
management.AssignDomainToField(featpoly, "F_Type", "FeaturePolygon")
management.AssignDomainToField(featpoint, "F_Type", "FeaturePoint")
management.AssignDomainToField(hist_art, "FS_Type", "HistoricArtifact")
management.AssignDomainToField(prehist_art, "FS_Type", "PrehistoricArtifact")

# Import project area into Project Feature Dataset
if projection != '':
	ape = management.Project(input_dataset, os.path.join(gdb, 'Project_Features', 'APE'), projection)

else:
	ape = conversion.FeatureClassToFeatureClass(input_dataset, os.path.join(gdb, 'Project_Features'), 'APE')

analysis.Buffer(ape, os.path.join(gdb, 'Project_Features', 'Research_Area'), "1 Mile")

# Create photo point feature class
AddMessage("Adding Extra Features...")
photopoint = management.CreateFeatureclass(gdb, "Photo_Point", "Point", '', '', '', spatial_ref)
[management.AddField(photopoint, "{}".format(i), "Text") for i in ["Photo_ID", "Cardinal_Dir", "Comment"]]
management.AssignDomainToField(photopoint, "Cardinal_Dir", "CardinalDir")

# Create GLO Features
for item in survey_features:
	feature = management.CreateFeatureclass(gdb, 'Class_I_Data\GLO_{}'.format(item), item, '', '', '', spatial_ref)
	[management.AddField(feature, i, "Text") for i in ['GLO_TYPE', 'GLO_NAME', 'GLO_DATE', 'RMS', 'TRANSFORM']]

# Create Project Centerpoint
center = management.CreateFeatureclass(gdb, "Project_Centerpoint", "Point", '', '', '', spatial_ref)

with da.SearchCursor(ape, "SHAPE@") as cursor:
	for row in cursor:
		centroid = row[0].centroid
		centroid = PointGeometry(centroid)
		with da.InsertCursor(center, "SHAPE@") as inscurs:
			inscurs.insertRow([centroid])
