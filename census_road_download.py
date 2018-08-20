from ftplib import FTP
from zipfile import ZipFile
import pandas as pd
import os

def create_folder(dir_location, folder_name):
	"""
	DOCSTRING: Creates a new folder if one doesn't already exist
	"""
	new_file = os.path.join(dir_location, folder_name)
	
	if not os.path.exists(new_file):
		os.mkdir(new_file)
		
	return new_file

def get_state_county_identifier(data_frame, index_location):
	"""
	DOCSTRING: Formats the 
	"""
	state_id = str(data_frame['State ANSI'].iloc[index_location]).zfill(2)
	county_id = str(data_frame['County ANSI'].iloc[index_location]).zfill(3)
	
	return state_id + county_id
	

def create_state_structure(state, dir_location):
	
	global df
	
	state_df = df[df['STATE_NAME'] == state]
	
	state_folder = create_folder(dir_location, state)
	
	counties = [i for i in state_df['County Name']]
	
	for i in range(len(counties)):
		county_folder = create_folder(state_folder, counties[i])
		
		outputZip = os.path.join(county_folder, 'tl_2017_{}_roads.zip'.format(get_state_county_identifier(state_df, i)))
		with open(outputZip, 'wb') as f:
			ftp.retrbinary('RETR ' + '{}'.format(outputZip), f.write)		


outputFolder = r'C:\Users\Mitchell.Fyock\Downloads\test'

Census_States = pd.DataFrame(pd.read_csv(r'C:\Users\Mitchell.Fyock\GIS_Resources\Docs\CENSUS_FIPS_STATE - Copy.txt'))
Census_Counties = pd.DataFrame(pd.read_csv(r'C:\Users\Mitchell.Fyock\GIS_Resources\Docs\CENSUS_FIPS_COUNTY - Copy.txt'))
df = Census_States.merge(Census_Counties, left_on="State", right_on="State ANSI")

states = [str(i) for i in Census_States['STATE_NAME']]

for state in states:
	ftp = FTP('ftp2.census.gov')
	ftp.connect()
	create_state_structure(state, outputFolder)
