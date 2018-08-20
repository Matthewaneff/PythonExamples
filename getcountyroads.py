import os
import time
import arcpy
from ftplib import FTP
from zipfile import ZipFile

county_ds = arcpy.GetParameterAsText(0)
output_workspace = arcpy.GetParameterAsText(1)

county_ids = []
county_names = []

with arcpy.da.SearchCursor(county_ds, "*") as cursor:
    for row in cursor:
        county_ids.append(str(row[2]) + str(row[3]))
        county_names.append(str(row[6]))

ftp = FTP('ftp2.census.gov')
ftp.login()
ftp.cwd('geo/tiger/TIGER2017/ROADS')

for index in range(len(county_ids)):

    county_id = county_ids[index]
    county_name = county_names[index]

    z = 'tl_2017_{}_roads.zip'.format(county_id)
    temp_location = r'C:\Users\Mitchell.Fyock\Downloads'

    download_dir = os.path.join(temp_location, z)

    with open(download_dir, 'wb') as f:
        ftp.retrbinary('RETR ' + '{}'.format(z), f.write)

    extract_dir = os.path.join(temp_location, z.split('.')[0])

    ZipFile(download_dir).extractall(extract_dir)

    road_file = os.path.join(extract_dir, 'tl_2017_{}_roads.shp'.format(county_id))

    arcpy.conversion.FeatureClassToFeatureClass(road_file, output_workspace, county_name)

    time.sleep(1)

ftp.quit()
ftp.close()
