import arcpy, csv, os
from arcpy import *

mxd =  mapping.MapDocument(r'C:\Users\Mitchell.Fyock\GIS_Resources\Templates\Location.mxd')
env.workspace = r'C:\Users\Mitchell.Fyock\GIS_Resources\Templates'

mxd.title = 'Title Test'
mxd.author = 'Ringle Dingle'

mxd.saveACopy(r'C:\Users\Mitchell.Fyock\GIS_Resources\Templates\Test.mxd')
