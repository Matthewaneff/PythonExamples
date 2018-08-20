import os, wget

if __name__=='__main__':
	url = 'ftp://ftp2.census.gov/geo/tiger/TIGER2017/PRISECROADS/tl_2017_02_prisecroads.zip'
	nFile = r'C:\Users\Mitchell.Fyock\Downloads'
	
	wget.download(url,out=nFile)
