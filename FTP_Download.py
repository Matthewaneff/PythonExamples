from ftplib import FTP
from zipfile import ZipFile

ftp = FTP('ftp2.census.gov')
ftp.connect()
ftp.login()
ftp.cwd('geo/tiger/TIGER2017/ROADS')

zipfile = 'tl_2017_19033_roads.zip'

outputLocation = r'C:\Users\Mitchell.Fyock\Downloads\{}'.format(zipfile)
with open(outputLocation, 'wb') as f:
	ftp.retrbinary('RETR ' + '{}'.format(zipfile), f.write)

unzipLocation = r'C:\Users\Mitchell.Fyock\Downloads\Cerro_Gordo_Roads'

ZipFile(outputLocation).extractall(unzipLocation)
